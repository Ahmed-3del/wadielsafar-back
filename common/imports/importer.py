"""Turning a filled-in spreadsheet into rows, through the API's own rules.

The point of doing it this way: a bulk import validates with exactly the
serializer the panel's own forms post through. There is no second definition of
what a valid hotel is, so an import cannot quietly write something the forms
would have refused.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.db import transaction

from common.imports.workbook import as_boolean


@dataclass
class RowError:
    """One thing wrong with one row, named the way the spreadsheet names it."""

    row: int
    column: str
    message: str


@dataclass
class ImportReport:
    created: int = 0
    updated: int = 0
    errors: list[RowError] = field(default_factory=list)
    # Filled in on a dry run so the panel can show what would happen.
    preview: list[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "created": self.created,
            "updated": self.updated,
            "errors": [
                {"row": error.row, "column": error.column, "message": error.message}
                for error in self.errors
            ],
            "preview": self.preview,
        }


class SpreadsheetImporter:
    """Validates every row first, writes only if all of them pass.

    All-or-nothing on purpose. A spreadsheet is one act to the person who sent
    it, and a half-applied one — 40 hotels in, 12 rejected, no way to tell which
    without reading a log — is worse than a refusal that says what to fix.
    """

    def __init__(self, *, serializer_class, queryset, key, columns, context, lookups=None):
        self.serializer_class = serializer_class
        self.queryset = queryset
        # One column or several. A visa type's name repeats across countries,
        # so matching on the name alone would update Turkey's tourist visa with
        # Georgia's row.
        self.key = (key,) if isinstance(key, str) else tuple(key)
        self.columns = {column["name"]: column for column in columns}
        self.context = context
        self.lookups = lookups or {}

    # ------------------------------------------------------------ coercion --

    def _coerce(self, name: str, value: str, row_number: int, errors: list[RowError]):
        """Spreadsheet text into something the serializer will accept."""
        column = self.columns.get(name, {})
        kind = column.get("type")

        if kind == "boolean":
            decided = as_boolean(value)
            if decided is None:
                errors.append(
                    RowError(row_number, name, f'"{value}" is not yes or no — write yes or no.')
                )
                return None
            return decided

        if kind == "list":
            # Several values in one cell, which is how a spreadsheet has to
            # carry them. Comma or Arabic comma, extra spaces forgiven.
            return [part.strip() for part in value.replace("،", ",").split(",") if part.strip()]

        if name in self.lookups:
            return self._resolve(name, value, row_number, errors)

        return value

    def _resolve(self, name: str, value: str, row_number: int, errors: list[RowError]):
        """A human-readable reference — a destination's name, a port's code —
        into the id the serializer wants.

        Nobody filling in a spreadsheet knows a database id, and asking for one
        is how an import ends up attached to the wrong city.
        """
        model, fields, many = self.lookups[name]
        wanted = [value] if not many else [part.strip() for part in value.replace("،", ",").split(",")]
        ids = []
        for term in [item for item in wanted if item]:
            match = None
            for lookup_field in fields:
                match = model.objects.filter(**{f"{lookup_field}__iexact": term}).first()
                if match:
                    break
            if match is None:
                errors.append(
                    RowError(
                        row_number,
                        name,
                        f'No {model._meta.verbose_name} called "{term}". '
                        f"Match one by {' or '.join(fields)}.",
                    )
                )
                return None
            ids.append(match.pk)
        return ids if many else (ids[0] if ids else None)

    def _match(self, row: dict, payload: dict):
        """The row this one replaces, if there is one.

        Matched on the key columns as the sheet spells them — case-insensitively,
        because "JED" and "jed" are the same airport to whoever typed them.
        A key column that resolves to a reference (a visa type's country) is
        matched on the id it resolved to.
        """
        filters = {}
        for column in self.key:
            raw = str(row.get(column, "")).strip()
            if not raw:
                return None
            field = self.columns.get(column, {}).get("field", column)
            if column in self.lookups:
                resolved = payload.get(field)
                if resolved is None:
                    return None
                filters[field.removesuffix("_id")] = resolved
            else:
                filters[f"{field}__iexact"] = raw
        return self.queryset.filter(**filters).first()

    # -------------------------------------------------------------- running --

    def run(self, rows: list[dict], *, dry_run: bool) -> ImportReport:
        report = ImportReport()
        if not rows:
            report.errors.append(RowError(0, "", "The sheet has no rows to import."))
            return report

        unknown = set(rows[0]) - set(self.columns)
        if unknown:
            # Named rather than ignored: a mistyped header silently dropping a
            # whole column is the failure people do not notice until later.
            report.errors.append(
                RowError(
                    1,
                    ", ".join(sorted(unknown)),
                    "This sheet has columns the import does not know. "
                    "Download the template and use its headers.",
                )
            )
            return report

        prepared = []
        for index, row in enumerate(rows, start=2):  # row 1 is the header
            payload, row_errors = {}, []
            for name, raw in row.items():
                if raw == "":
                    continue
                value = self._coerce(name, raw, index, row_errors)
                if value is not None:
                    payload[self.columns[name].get("field", name)] = value
            report.errors.extend(row_errors)
            if row_errors:
                continue

            instance = self._match(row, payload)
            serializer = self.serializer_class(
                instance=instance, data=payload, partial=instance is not None, context=self.context
            )
            if not serializer.is_valid():
                for column, messages in serializer.errors.items():
                    text = messages[0] if isinstance(messages, list) else str(messages)
                    report.errors.append(RowError(index, str(column), str(text)))
                continue

            prepared.append((serializer, instance))
            if instance:
                report.updated += 1
            else:
                report.created += 1
            report.preview.append(
                {
                    "row": index,
                    "key": " · ".join(str(row.get(column, "")) for column in self.key),
                    "action": "update" if instance else "create",
                }
            )

        if not report.ok or dry_run:
            # Nothing is written on a failed or rehearsed run, so the counts
            # above describe what *would* happen.
            if not report.ok:
                report.created = report.updated = 0
                report.preview = []
            return report

        with transaction.atomic():
            for serializer, _ in prepared:
                serializer.save()
        return report

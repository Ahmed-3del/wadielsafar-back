"""The two endpoints a bulk-importable resource gets.

    GET  /api/v1/<resource>/import-template/   the spreadsheet to fill in
    POST /api/v1/<resource>/import/            send it back

Added to a viewset by mixing this in and declaring `import_columns`. Everything
else — permissions, validation, what a valid row even is — comes from the
viewset and serializer that were already there.
"""

from __future__ import annotations

from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response

from common.imports.importer import SpreadsheetImporter
from common.imports.workbook import SpreadsheetError, build_template, read_rows
from common.permissions import IsContentManager

MAX_ROWS = 5000
MAX_BYTES = 10 * 1024 * 1024

NOTES = [
    "Fill in one row per record and upload this file in the panel.",
    "A column marked * is required when creating something new.",
    "Rows are matched on the key column: a row whose key already exists is",
    "updated, and a row whose key is new is created. Nothing is ever deleted.",
    "Yes/no columns accept yes, no, true, false, 1, 0, نعم or لا.",
    "Dates are yyyy-mm-dd. A date cell formatted as a date works too.",
    "If any row is wrong, nothing at all is saved and the panel lists what to fix.",
]


class BulkImportMixin:
    """Declare these on the viewset:

    `import_columns`   the spreadsheet's columns, in order. Each is a dict:
                       name (the header), required, help, and optionally
                       type ("boolean" / "list") or field (the serializer's
                       name for it, when the header should read differently).
    `import_key`       the column rows are matched on. Its value is what
                       decides update-or-create.
    `import_lookups`   columns holding a human reference rather than an id:
                       {column: (Model, (fields to try), many)}.
    """

    import_columns: list[dict] = []
    import_key: str = ""
    import_lookups: dict = {}

    def _key_label(self) -> str:
        key = self.import_key
        return key if isinstance(key, str) else " + ".join(key)

    def _import_context(self):
        return {"request": self.request, "view": self, "format": self.format_kwarg}

    def _model(self):
        return self.get_serializer_class().Meta.model

    # Gated like the upload it goes with. The template holds no data, but it is
    # a tool for whoever maintains the catalogue, not part of the public API.
    @action(
        detail=False,
        methods=["get"],
        url_path="import-template",
        permission_classes=[IsContentManager],
    )
    def import_template(self, request):
        name = str(self._model()._meta.verbose_name_plural)
        content = build_template(
            self.import_columns,
            sheet_title=name.title(),
            notes=[*NOTES, "", f"Rows are matched on: {self._key_label()}."],
        )
        response = HttpResponse(
            content,
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        filename = name.replace(" ", "-").lower()
        response["Content-Disposition"] = f'attachment; filename="{filename}-template.xlsx"'
        return response

    @action(detail=False, methods=["post"], url_path="import")
    def import_rows(self, request):
        uploaded = request.FILES.get("file")
        if uploaded is None:
            return Response({"detail": "Attach the filled-in spreadsheet as `file`."}, status=400)
        if uploaded.size > MAX_BYTES:
            return Response(
                {"detail": "That file is larger than 10MB. Split it into a few sheets."},
                status=400,
            )

        try:
            rows = read_rows(uploaded)
        except SpreadsheetError as error:
            return Response({"detail": str(error)}, status=400)

        if len(rows) > MAX_ROWS:
            return Response(
                {
                    "detail": (
                        f"{len(rows)} rows is more than one import can take "
                        f"({MAX_ROWS}). Split it into a few sheets."
                    )
                },
                status=400,
            )

        # Import writes, so it reads and writes against everything — not the
        # public queryset, which hides whatever is switched off and would make
        # a re-import duplicate the rows it cannot see.
        importer = SpreadsheetImporter(
            serializer_class=self.get_serializer_class(),
            queryset=self._model().objects.all(),
            key=self.import_key,
            columns=self.import_columns,
            context=self._import_context(),
            lookups=self.import_lookups,
        )
        report = importer.run(rows, dry_run=str(request.data.get("dry_run", "")).lower() == "true")
        return Response(report.as_dict(), status=200 if report.ok else 400)

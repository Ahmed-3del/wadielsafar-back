"""Reading and writing the spreadsheets the panel's bulk import uses.

Kept apart from the import logic so the awkward parts of a real spreadsheet —
a header nobody spelled the way the code expects, a date Excel handed over as a
datetime, a "1" that means yes — are solved once rather than per resource.
"""

from __future__ import annotations

import csv
import datetime as dt
import io

from openpyxl import Workbook, load_workbook

# What people actually type when they mean yes or no, in both languages.
TRUE_WORDS = {"true", "yes", "y", "1", "نعم", "صح", "مفعل", "نشط"}
FALSE_WORDS = {"false", "no", "n", "0", "لا", "خطأ", "معطل", "غير نشط"}


class SpreadsheetError(Exception):
    """The file could not be read at all — not a problem with one row."""


def _clean_header(value) -> str:
    """Headers get typed by hand, so match them loosely: case, stray spaces and
    a trailing asterisk (which the template uses to mark a required column) all
    stop mattering."""
    return str(value or "").strip().lstrip("*").rstrip("*").strip().lower().replace(" ", "_")


def _clean_cell(value):
    if value is None:
        return ""
    if isinstance(value, dt.datetime):
        # Excel hands back midnight datetimes for plain dates; the API wants a
        # date, and "2026-01-05 00:00:00" is not one it accepts.
        return value.date().isoformat() if value.time() == dt.time.min else value.isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        # openpyxl reads every number as a float, which turns a 5-star rating
        # into "5.0" and a phone number into something nobody can dial.
        return str(int(value))
    return str(value).strip()


def read_rows(uploaded_file) -> list[dict[str, str]]:
    """Every row of the first sheet, keyed by its cleaned header.

    Accepts .xlsx and .csv, because half the people sending a "sheet" send a
    CSV exported from one.
    """
    name = (getattr(uploaded_file, "name", "") or "").lower()
    if name.endswith(".csv"):
        return _read_csv(uploaded_file)
    return _read_xlsx(uploaded_file)


def _read_csv(uploaded_file) -> list[dict[str, str]]:
    raw = uploaded_file.read()
    if isinstance(raw, bytes):
        # utf-8-sig, because a CSV saved out of Excel begins with a BOM and the
        # first column header would otherwise never match anything.
        for encoding in ("utf-8-sig", "utf-16", "cp1256"):
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise SpreadsheetError("The file is not text this can read. Save it as .xlsx.")
    else:
        text = raw

    reader = csv.reader(io.StringIO(text))
    try:
        header = [_clean_header(cell) for cell in next(reader)]
    except StopIteration:
        return []
    return [
        {key: _clean_cell(value) for key, value in zip(header, row, strict=False) if key}
        for row in reader
        if any(str(cell).strip() for cell in row)
    ]


def _read_xlsx(uploaded_file) -> list[dict[str, str]]:
    try:
        workbook = load_workbook(uploaded_file, read_only=True, data_only=True)
    except Exception as error:  # openpyxl raises a zoo of exception types
        raise SpreadsheetError(
            "That file could not be opened as a spreadsheet. Save it as .xlsx or .csv."
        ) from error

    sheet = workbook.worksheets[0]
    rows = sheet.iter_rows(values_only=True)
    try:
        header = [_clean_header(cell) for cell in next(rows)]
    except StopIteration:
        return []

    out = []
    for row in rows:
        if not any(cell is not None and str(cell).strip() for cell in row):
            continue  # a blank line in the middle is not a row
        out.append(
            {key: _clean_cell(value) for key, value in zip(header, row, strict=False) if key}
        )
    workbook.close()
    return out


def as_boolean(value: str) -> bool | None:
    """None when the cell says something that is neither."""
    text = str(value).strip().lower()
    if text in TRUE_WORDS:
        return True
    if text in FALSE_WORDS:
        return False
    return None


def build_template(columns: list[dict], sheet_title: str, notes: list[str]) -> bytes:
    """A workbook with the headers to fill in, and a second sheet explaining
    them.

    The explanation is on its own sheet rather than in a comment row, so the
    file can be filled in and sent straight back without deleting anything.
    """
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_title[:31] or "Import"

    for index, column in enumerate(columns, start=1):
        cell = sheet.cell(row=1, column=index)
        cell.value = column["name"] + ("*" if column.get("required") else "")
        sheet.column_dimensions[cell.column_letter].width = max(14, min(38, len(cell.value) + 6))

    guide = workbook.create_sheet("How to fill this in")
    guide.column_dimensions["A"].width = 26
    guide.column_dimensions["B"].width = 14
    guide.column_dimensions["C"].width = 90
    for index, line in enumerate(notes, start=1):
        guide.cell(row=index, column=1).value = line
    start = len(notes) + 2
    for label, index in (("Column", 1), ("Required", 2), ("What goes in it", 3)):
        guide.cell(row=start, column=index).value = label
    for offset, column in enumerate(columns, start=1):
        guide.cell(row=start + offset, column=1).value = column["name"]
        guide.cell(row=start + offset, column=2).value = "yes" if column.get("required") else ""
        guide.cell(row=start + offset, column=3).value = column.get("help", "")

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()

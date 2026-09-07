"""The shipped airport catalogue.

Reference data: IATA code, airport name, city and country. Nothing here asserts
anything about the company — no routes, no prices, no airline relationships —
so it is safe to ship and safe to re-apply.

The rows live in airports.csv next door rather than in this file. At four
thousand airports a Python tuple stopped being something anyone could read or
review: a one-airport correction showed up in a diff as a line lost in eight
hundred kilobytes of source. The CSV is the same eight columns, one airport per
line, and it is generated — see build_catalogue.py for where each column comes
from and why a rebuild cannot overwrite a hand-checked Arabic name.

Each row is:
    (iata, name_en, name_ar, city_en, city_ar, country_en, country_ar, cc)

`POPULAR` lists the codes the picker offers before the traveller types: Saudi
departure points first, then the destinations most asked for from here.
"""

import csv
from pathlib import Path

from common.utilities import normalize_arabic, normalize_latin

POPULAR = ("JED", "RUH", "DMM", "MED", "DXB", "DOH", "CAI", "IST", "LHR", "KUL", "BKK", "AMM")

DATA_FILE = Path(__file__).resolve().parent / "airports.csv"


def _load() -> tuple[tuple[str, str, str, str, str, str, str, str], ...]:
    with DATA_FILE.open(encoding="utf-8", newline="") as handle:
        return tuple(
            (
                row["iata"],
                row["name_en"],
                row["name_ar"],
                row["city_en"],
                row["city_ar"],
                row["country_en"],
                row["country_ar"],
                row["cc"],
            )
            for row in csv.DictReader(handle)
        )


AIRPORTS: tuple[tuple[str, str, str, str, str, str, str, str], ...] = _load()


def sync(airport_model) -> tuple[int, int]:
    """Upsert the catalogue, keyed on IATA code.

    Takes the model class as an argument so a migration can hand in its
    historical version. Idempotent: re-running refreshes names and leaves any
    `is_active` an agent has changed alone, because switching an airport off is
    an editorial decision and a re-seed has no business overriding it.

    Returns (created, updated).
    """
    # Written in batches rather than one query per airport. At four thousand
    # rows the row-at-a-time version took minutes against a network database —
    # long enough that an operator assumes it has hung and interrupts it.
    #
    # bulk_create and bulk_update do not call save(), so the two things save()
    # would have done are done here instead: upper-casing the codes, and
    # folding the Arabic that the picker searches on. Miss the folding and
    # every airport added today is invisible to an Arabic search.
    columns = [
        "name_en",
        "name_ar",
        "city_en",
        "city_ar",
        "country_en",
        "country_ar",
        "country_code",
        "is_popular",
        "order",
    ]
    # Migration 0002 hands in a historical model from before either pair of
    # folded columns existed; 0003 and 0004 add them and backfill what 0002
    # wrote. Checked separately because they arrived one migration apart.
    present = {field.name for field in airport_model._meta.get_fields()}
    has_arabic_fold = present >= {"city_ar_folded", "text_ar_folded"}
    has_latin_fold = present >= {"city_en_folded", "text_en_folded"}
    if has_arabic_fold:
        columns += ["city_ar_folded", "text_ar_folded"]
    if has_latin_fold:
        columns += ["city_en_folded", "text_en_folded"]

    existing = {airport.iata_code: airport for airport in airport_model.objects.all()}
    to_create, to_update = [], []

    for order, row in enumerate(AIRPORTS):
        iata, name_en, name_ar, city_en, city_ar, country_en, country_ar, cc = row
        iata = iata.upper()
        fields = {
            "name_en": name_en,
            "name_ar": name_ar,
            "city_en": city_en,
            "city_ar": city_ar,
            "country_en": country_en,
            "country_ar": country_ar,
            "country_code": cc.upper(),
            "is_popular": iata in POPULAR,
            "order": POPULAR.index(iata) if iata in POPULAR else order + 100,
        }
        if has_arabic_fold:
            fields["city_ar_folded"] = normalize_arabic(city_ar)
            fields["text_ar_folded"] = normalize_arabic(f"{name_ar} {country_ar}")
        if has_latin_fold:
            fields["city_en_folded"] = normalize_latin(city_en)
            fields["text_en_folded"] = normalize_latin(f"{name_en} {country_en}")

        airport = existing.get(iata)
        if airport is None:
            to_create.append(airport_model(iata_code=iata, **fields))
        else:
            for column, value in fields.items():
                setattr(airport, column, value)
            to_update.append(airport)

    airport_model.objects.bulk_create(to_create, batch_size=500)
    airport_model.objects.bulk_update(to_update, columns, batch_size=500)
    return len(to_create), len(to_update)

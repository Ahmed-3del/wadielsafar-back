"""The shipped cruise-port catalogue.

Reference data: the port, the city it serves, and the country it sits in.
Nothing here asserts anything about the company — no sailings, no prices, no
cruise line relationships — so it is safe to ship and safe to re-apply.

The rows live in ports.csv next door rather than in this file, the same way the
airport catalogue is arranged and for the same reason. build_catalogue.py says
where they come from and why every one of them is checked against a source
before it is written.

Each row is:
    (code, name_en, name_ar, city_en, city_ar, country_en, country_ar, cc)

The homepage asks for a country and then one of its ports, so the country
columns are what group the list. They are spelt the way the airport catalogue
and the panel's country picker spell them, which is how a country ends up with
one group rather than two.

`POPULAR` is what the picker offers before anyone types: where this market
sails from, then the home ports its travellers fly out to join.
"""

import csv
from pathlib import Path

from common.utilities import normalize_arabic, normalize_latin

POPULAR = (
    "jeddah",
    "dubai-port-rashid",
    "abu-dhabi-zayed",
    "doha",
    "bahrain",
    "muscat",
    "aqaba",
    "barcelona",
    "civitavecchia",
    "istanbul-port",
    "piraeus",
    "singapore-port",
)

DATA_FILE = Path(__file__).resolve().parent / "ports.csv"


def _load() -> tuple[tuple[str, str, str, str, str, str, str, str], ...]:
    with DATA_FILE.open(encoding="utf-8", newline="") as handle:
        return tuple(
            (
                row["code"],
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


PORTS: tuple[tuple[str, str, str, str, str, str, str, str], ...] = _load()


def sync(CruisePort) -> tuple[int, int]:
    """Load or refresh the catalogue. Safe to re-run.

    Matched on `code`, so re-running updates a port in place rather than
    duplicating it — and an editor's own row, added in the panel with a code of
    its own, is left alone.

    Written in batches, and the two things save() would have done are done here
    instead: upper-casing the country code, and folding the text the picker
    searches on. Miss the folding and a port added today cannot be found by
    typing its name.
    """
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
    present = {field.name for field in CruisePort._meta.get_fields()}
    has_arabic_fold = present >= {"city_ar_folded", "text_ar_folded"}
    has_latin_fold = present >= {"city_en_folded", "text_en_folded"}
    if has_arabic_fold:
        columns += ["city_ar_folded", "text_ar_folded"]
    if has_latin_fold:
        columns += ["city_en_folded", "text_en_folded"]

    existing = {port.code: port for port in CruisePort.objects.all()}
    to_create, to_update = [], []

    for order, row in enumerate(PORTS):
        code, name_en, name_ar, city_en, city_ar, country_en, country_ar, cc = row
        fields = {
            "name_en": name_en,
            "name_ar": name_ar,
            "city_en": city_en,
            "city_ar": city_ar,
            "country_en": country_en,
            "country_ar": country_ar,
            "country_code": cc.upper(),
            "is_popular": code in POPULAR,
            "order": POPULAR.index(code) if code in POPULAR else order + 100,
        }
        if has_arabic_fold:
            fields["city_ar_folded"] = normalize_arabic(city_ar)
            fields["text_ar_folded"] = normalize_arabic(f"{name_ar} {country_ar}")
        if has_latin_fold:
            fields["city_en_folded"] = normalize_latin(city_en)
            fields["text_en_folded"] = normalize_latin(f"{name_en} {country_en}")

        port = existing.get(code)
        if port is None:
            to_create.append(CruisePort(code=code, **fields))
        else:
            for column, value in fields.items():
                setattr(port, column, value)
            to_update.append(port)

    CruisePort.objects.bulk_create(to_create, batch_size=500)
    CruisePort.objects.bulk_update(to_update, columns, batch_size=500)
    return len(to_create), len(to_update)

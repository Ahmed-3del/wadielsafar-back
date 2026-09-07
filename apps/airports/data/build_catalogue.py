"""Regenerates airports.csv. A developer tool — nothing imports it at runtime.

    python apps/airports/data/build_catalogue.py

Three sources, none of them this file's own memory:

  OurAirports   every airport with an IATA code and scheduled passenger
                service. Public domain, refreshed daily.
  Wikidata      Arabic names for the airport and the city it serves, where
                anyone has written one.
  CLDR          Arabic country names, read through Node's Intl.DisplayNames —
                the same source the panel's country picker is generated from,
                so a country is spelt one way across the whole product.

Two rules keep a regeneration from undoing editorial work:

  * Names already in airports.csv win. The first 259 rows were written and
    checked by hand; Wikidata must not overwrite "مطار الملك عبدالعزيز الدولي"
    with something a stranger typed.
  * Where nothing has an Arabic name, the Arabic column carries the English
    one. Inventing an Arabic name for an airport nobody has named is how a
    picker ends up offering a place that does not exist under that name.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "airports.csv"

OURAIRPORTS = "https://davidmegginson.github.io/ourairports-data/airports.csv"
WIKIDATA = "https://query.wikidata.org/sparql"
UA = "WadiAlSafar-catalogue-build/1.0 (https://wadialsafar.com)"

# Airports a traveller can actually book a seat to. Everything else in the
# source — the 82,000 airfields, heliports and seaplane bases with no timetable
# — would bury the ten they meant in a picker.
KEEP_TYPES = {"large_airport", "medium_airport", "small_airport"}

# Asked as two small queries rather than one join. The combined form runs close
# enough to Wikidata's sixty-second ceiling that it sometimes answers 200 with
# a truncated body — valid-looking output, silently missing half the language.
AIRPORT_NAMES = """
SELECT ?iata ?label WHERE {
  ?airport wdt:P238 ?iata .
  ?airport rdfs:label ?label . FILTER(lang(?label) = "ar")
}
"""

CITY_NAMES = """
SELECT ?iata ?label WHERE {
  ?airport wdt:P238 ?iata .
  ?airport wdt:P931 ?city .
  ?city rdfs:label ?label . FILTER(lang(?label) = "ar")
}
"""

# The public endpoint is shared and rate limited; a 502 or a truncated body is
# ordinary rather than exceptional, and the answer is to ask again.
ATTEMPTS = 5

FIELDS = ("iata", "name_en", "name_ar", "city_en", "city_ar", "country_en", "country_ar", "cc")


def fetch(url: str, params: dict | None = None, accept: str | None = None) -> bytes:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    if accept:
        request.add_header("Accept", accept)
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def wikidata_labels(query: str) -> dict[str, str]:
    """One IATA code to one Arabic label.

    Retried, because a partial answer here is worse than no answer: it would
    look like a successful build that had quietly lost half the Arabic.
    """
    last = ""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            body = fetch(
                WIKIDATA,
                {"query": query, "format": "json"},
                accept="application/sparql-results+json",
            )
            bindings = json.loads(body)["results"]["bindings"]
        except (json.JSONDecodeError, OSError) as error:
            last = str(error)
            print(f"  attempt {attempt}/{ATTEMPTS} failed ({error}); retrying…")
            time.sleep(5 * attempt)
            continue
        return {
            binding["iata"]["value"].strip().upper(): binding["label"]["value"].strip()
            for binding in reversed(bindings)
        }
    raise SystemExit(f"Wikidata did not answer after {ATTEMPTS} attempts: {last}")


def country_names() -> dict[str, tuple[str, str]]:
    """CLDR country names in both languages, via Node."""
    script = """
    const en = new Intl.DisplayNames(['en'], { type: 'region' });
    const ar = new Intl.DisplayNames(['ar'], { type: 'region' });
    const out = {};
    for (let a = 65; a <= 90; a++) for (let b = 65; b <= 90; b++) {
      const code = String.fromCharCode(a) + String.fromCharCode(b);
      if (en.of(code) === code) continue;
      out[code] = [en.of(code), ar.of(code)];
    }
    process.stdout.write(JSON.stringify(out));
    """
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=True
    )
    return {code: tuple(names) for code, names in json.loads(result.stdout).items()}


def existing_rows() -> dict[str, dict[str, str]]:
    """What airports.csv already says, keyed on IATA code."""
    if not OUT.exists():
        return {}
    with OUT.open(encoding="utf-8", newline="") as handle:
        return {row["iata"]: row for row in csv.DictReader(handle)}


def house_style(existing: dict[str, dict[str, str]]) -> dict[str, tuple[str, str]]:
    """How this catalogue already spells a country.

    CLDR says "المملكة العربية السعودية" where this catalogue says "السعودية",
    and the cruise search groups ports by that string — so two spellings means
    one country listed twice. Whatever is already here wins.
    """
    return {
        row["cc"]: (row["country_en"], row["country_ar"])
        for row in existing.values()
        if row["cc"] and row["country_ar"]
    }


def main() -> int:
    existing = existing_rows()
    print(f"airports.csv currently holds {len(existing)} rows")

    print("fetching OurAirports…")
    source = list(csv.DictReader(fetch(OURAIRPORTS).decode("utf-8").splitlines()))
    airports = [
        row
        for row in source
        if row["scheduled_service"] == "yes"
        and row["type"] in KEEP_TYPES
        and len(row["iata_code"].strip()) == 3
    ]
    print(f"  {len(airports)} airports with a timetable and an IATA code")

    print("fetching Arabic names from Wikidata…")
    airport_ar = wikidata_labels(AIRPORT_NAMES)
    city_ar = wikidata_labels(CITY_NAMES)
    print(f"  {len(airport_ar)} Arabic airport names, {len(city_ar)} Arabic city names")

    countries = country_names()
    preferred = house_style(existing)

    rows, kept, no_arabic = [], 0, 0
    for airport in sorted(airports, key=lambda r: (r["iso_country"], r["iata_code"])):
        code = airport["iata_code"].strip().upper()
        cc = airport["iso_country"].strip().upper()
        was = existing.get(code)

        name_en = (was or {}).get("name_en") or airport["name"].strip()
        city_en = (was or {}).get("city_en") or airport["municipality"].strip() or name_en

        # A hand-checked Arabic name is worth more than a fetched one, and a
        # fetched one is worth more than the English fallback.
        name_ar = (was or {}).get("name_ar", "")
        if not name_ar or name_ar == name_en:
            name_ar = airport_ar.get(code, "") or name_en
        arabic_city = (was or {}).get("city_ar", "")
        if not arabic_city or arabic_city == city_en:
            arabic_city = city_ar.get(code, "") or city_en

        if was:
            kept += 1
        if name_ar == name_en:
            no_arabic += 1

        country_en, country_ar = preferred.get(cc) or countries.get(cc) or (cc, cc)
        rows.append(
            dict(
                zip(
                    FIELDS,
                    (code, name_en, name_ar, city_en, arabic_city, country_en, country_ar, cc),
                    strict=True,
                )
            )
        )

    # One row per IATA code: the source carries a handful of duplicates where
    # two fields share one code, and the seeder keys on it.
    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        seen.setdefault(row["iata"], row)

    # A rebuild must never quietly lose an airport somebody added on purpose.
    # OurAirports drops a field the day its last timetabled flight goes, and
    # Khamis Mushait and Phnom Penh are not less bookable for that.
    carried = [row for code, row in existing.items() if code not in seen]
    for row in carried:
        seen[row["iata"]] = row
    if carried:
        print(
            "  carried over "
            + ", ".join(sorted(row["iata"] for row in carried))
            + " — in this catalogue but not in the source"
        )

    rows = [seen[code] for code in sorted(seen)]

    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    countries_covered = len({row["cc"] for row in rows})
    print(
        f"\nwrote {len(rows)} airports across {countries_covered} countries to {OUT.name}\n"
        f"  {kept} rows already present, names preserved\n"
        f"  {no_arabic} carry the English name in the Arabic column (nobody has named them in Arabic)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

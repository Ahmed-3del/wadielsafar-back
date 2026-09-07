"""Regenerates ports.csv. A developer tool — nothing imports it at runtime.

    python apps/cruises/data/build_catalogue.py

Cruise ports are not like airports. There is no OurAirports for them: no open
dataset says "these are the places cruise ships sail from". Wikidata knows
eleven thousand "ports", and they are dredging berths, fishing harbours, naval
bases and whole coastal cities — a picker built from that would offer
Guantanamo Bay under "departure port".

So this list is curated rather than downloaded: CANDIDATES below is the ports a
cruise actually leaves from or calls at. What is *not* curated is any of the
detail — every candidate is checked against Wikidata, which supplies the
Arabic name and confirms the place exists in the country claimed for it. A
candidate Wikidata cannot confirm is dropped and named in the output rather
than written on trust.

The port's own name follows the house style already in ports.csv: "Port of
Split" / "ميناء سبليت". That is a description of a real place, built from a
verified city name — not a proper noun invented for a terminal nobody named.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "ports.csv"

WIKIDATA = "https://query.wikidata.org/sparql"
UA = "WadiAlSafar-catalogue-build/1.0 (https://wadialsafar.com)"
ATTEMPTS = 5
CHUNK = 60

FIELDS = ("code", "name_en", "name_ar", "city_en", "city_ar", "country_en", "country_ar", "cc")

# (city as Wikidata spells it in English, ISO 3166-1 alpha-2).
#
# Grouped by cruising region, which is how the itineraries that use them are
# sold. Every one of these is somewhere a cruise embarks or calls; none of them
# is here because it is a big port.
CANDIDATES: tuple[tuple[str, str], ...] = (
    # ---- Arabian Gulf and Red Sea ----------------------------------------
    ("Jeddah", "SA"), ("Yanbu", "SA"), ("Dammam", "SA"), ("Duba", "SA"),
    ("Dubai", "AE"), ("Abu Dhabi", "AE"), ("Sharjah", "AE"), ("Fujairah", "AE"),
    ("Doha", "QA"), ("Manama", "BH"), ("Kuwait City", "KW"),
    ("Muscat", "OM"), ("Salalah", "OM"), ("Khasab", "OM"), ("Sur", "OM"),
    ("Aqaba", "JO"), ("Safaga", "EG"), ("Sharm El Sheikh", "EG"),
    ("Alexandria", "EG"), ("Port Said", "EG"), ("Ain Sokhna", "EG"),
    ("Djibouti", "DJ"), ("Massawa", "ER"),
    # ---- Mediterranean ----------------------------------------------------
    ("Barcelona", "ES"), ("Valencia", "ES"), ("Málaga", "ES"), ("Cádiz", "ES"),
    ("Palma de Mallorca", "ES"), ("Ibiza", "ES"), ("Cartagena", "ES"),
    ("Alicante", "ES"), ("Bilbao", "ES"), ("Vigo", "ES"), ("A Coruña", "ES"),
    ("Santa Cruz de Tenerife", "ES"), ("Las Palmas de Gran Canaria", "ES"),
    ("Lanzarote", "ES"), ("Marseille", "FR"), ("Nice", "FR"), ("Toulon", "FR"),
    ("Ajaccio", "FR"), ("Bastia", "FR"), ("Cannes", "FR"), ("Sète", "FR"),
    ("Civitavecchia", "IT"), ("Genoa", "IT"), ("Naples", "IT"), ("Venice", "IT"),
    ("Trieste", "IT"), ("Savona", "IT"), ("Palermo", "IT"), ("Bari", "IT"),
    ("Livorno", "IT"), ("La Spezia", "IT"), ("Messina", "IT"), ("Catania", "IT"),
    ("Salerno", "IT"), ("Ravenna", "IT"), ("Cagliari", "IT"), ("Olbia", "IT"),
    ("Piraeus", "GR"), ("Santorini", "GR"), ("Mykonos", "GR"), ("Rhodes", "GR"),
    ("Heraklion", "GR"), ("Corfu", "GR"), ("Katakolo", "GR"), ("Volos", "GR"),
    ("Thessaloniki", "GR"), ("Chania", "GR"), ("Patmos", "GR"), ("Kos", "GR"),
    ("Istanbul", "TR"), ("Kuşadası", "TR"), ("Bodrum", "TR"), ("İzmir", "TR"),
    ("Antalya", "TR"), ("Marmaris", "TR"), ("Alanya", "TR"), ("Trabzon", "TR"),
    ("Valletta", "MT"), ("Limassol", "CY"), ("Larnaca", "CY"),
    ("Dubrovnik", "HR"), ("Split", "HR"), ("Zadar", "HR"), ("Rijeka", "HR"),
    ("Kotor", "ME"), ("Bar", "ME"), ("Durrës", "AL"), ("Koper", "SI"),
    ("Monaco", "MC"), ("Tunis", "TN"), ("Casablanca", "MA"), ("Tangier", "MA"),
    ("Agadir", "MA"), ("Funchal", "PT"), ("Lisbon", "PT"), ("Porto", "PT"),
    ("Ponta Delgada", "PT"), ("Gibraltar", "GI"), ("Haifa", "IL"),
    # ---- Northern Europe and the Baltic -----------------------------------
    ("Southampton", "GB"), ("Dover", "GB"), ("Edinburgh", "GB"),
    ("Liverpool", "GB"), ("Portsmouth", "GB"), ("Belfast", "GB"),
    ("Glasgow", "GB"), ("Newcastle upon Tyne", "GB"), ("Harwich", "GB"),
    ("Dublin", "IE"), ("Cork", "IE"), ("Amsterdam", "NL"), ("Rotterdam", "NL"),
    ("Zeebrugge", "BE"), ("Hamburg", "DE"), ("Kiel", "DE"), ("Warnemünde", "DE"),
    ("Bremerhaven", "DE"), ("Copenhagen", "DK"), ("Aarhus", "DK"),
    ("Oslo", "NO"), ("Bergen", "NO"), ("Tromsø", "NO"), ("Stavanger", "NO"),
    ("Ålesund", "NO"), ("Trondheim", "NO"), ("Kirkenes", "NO"),
    ("Longyearbyen", "NO"), ("Stockholm", "SE"), ("Gothenburg", "SE"),
    ("Visby", "SE"), ("Helsinki", "FI"), ("Turku", "FI"), ("Tallinn", "EE"),
    ("Riga", "LV"), ("Klaipėda", "LT"), ("Gdańsk", "PL"), ("Gdynia", "PL"),
    ("Reykjavík", "IS"), ("Akureyri", "IS"), ("Tórshavn", "FO"),
    ("Nuuk", "GL"), ("Saint Petersburg", "RU"),
    # ---- Caribbean, Mexico and Central America ----------------------------
    ("Nassau", "BS"), ("Freeport", "BS"), ("Bridgetown", "BB"),
    ("San Juan", "PR"), ("Philipsburg", "SX"), ("Oranjestad", "AW"),
    ("Willemstad", "CW"), ("Kralendijk", "BQ"), ("Castries", "LC"),
    ("St. George's", "GD"), ("Kingstown", "VC"), ("Roseau", "DM"),
    ("Basseterre", "KN"), ("St. John's", "AG"), ("Road Town", "VG"),
    ("Charlotte Amalie", "VI"), ("Fort-de-France", "MQ"), ("Pointe-à-Pitre", "GP"),
    ("George Town", "KY"), ("Montego Bay", "JM"), ("Ocho Rios", "JM"),
    ("Falmouth", "JM"), ("Santo Domingo", "DO"), ("La Romana", "DO"),
    ("Puerto Plata", "DO"), ("Havana", "CU"), ("Cozumel", "MX"),
    ("Progreso", "MX"), ("Ensenada", "MX"), ("Cabo San Lucas", "MX"),
    ("Puerto Vallarta", "MX"), ("Mazatlán", "MX"), ("Belize City", "BZ"),
    ("Roatán", "HN"), ("Colón", "PA"), ("Puerto Limón", "CR"),
    ("Cartagena", "CO"), ("Santa Marta", "CO"), ("Oranjestad", "AW"),
    # ---- North America ----------------------------------------------------
    ("Miami", "US"), ("Fort Lauderdale", "US"), ("Port Canaveral", "US"),
    ("Tampa", "US"), ("Galveston", "US"), ("New Orleans", "US"),
    ("New York City", "US"), ("Bayonne", "US"), ("Baltimore", "US"),
    ("Boston", "US"), ("Charleston", "US"), ("Norfolk", "US"),
    ("Seattle", "US"), ("Los Angeles", "US"), ("San Diego", "US"),
    ("San Francisco", "US"), ("Juneau", "US"), ("Ketchikan", "US"),
    ("Skagway", "US"), ("Sitka", "US"), ("Seward", "US"), ("Whittier", "US"),
    ("Honolulu", "US"), ("Vancouver", "CA"), ("Montreal", "CA"),
    ("Quebec City", "CA"), ("Halifax", "CA"), ("Saint John", "CA"),
    ("Victoria", "CA"),
    # ---- Asia and the Indian Ocean ----------------------------------------
    ("Singapore", "SG"), ("Port Klang", "MY"), ("Penang", "MY"),
    ("Kota Kinabalu", "MY"), ("Langkawi", "MY"), ("Phuket", "TH"),
    ("Laem Chabang", "TH"), ("Ko Samui", "TH"), ("Ho Chi Minh City", "VN"),
    ("Da Nang", "VN"), ("Ha Long", "VN"), ("Sihanoukville", "KH"),
    ("Hong Kong", "HK"), ("Shanghai", "CN"), ("Tianjin", "CN"),
    ("Xiamen", "CN"), ("Sanya", "CN"), ("Keelung", "TW"), ("Kaohsiung", "TW"),
    ("Yokohama", "JP"), ("Kobe", "JP"), ("Nagasaki", "JP"), ("Okinawa", "JP"),
    ("Hakodate", "JP"), ("Busan", "KR"), ("Incheon", "KR"), ("Jeju City", "KR"),
    ("Manila", "PH"), ("Boracay", "PH"), ("Bali", "ID"), ("Jakarta", "ID"),
    ("Surabaya", "ID"), ("Komodo", "ID"), ("Mumbai", "IN"), ("Kochi", "IN"),
    ("Goa", "IN"), ("Chennai", "IN"), ("Colombo", "LK"), ("Malé", "MV"),
    ("Port Louis", "MU"), ("Victoria", "SC"), ("Zanzibar City", "TZ"),
    ("Mombasa", "KE"), ("Nosy Be", "MG"),
    # ---- Africa, Oceania and South America --------------------------------
    ("Cape Town", "ZA"), ("Durban", "ZA"), ("Port Elizabeth", "ZA"),
    ("Walvis Bay", "NA"), ("Dakar", "SN"), ("Praia", "CV"),
    ("Sydney", "AU"), ("Brisbane", "AU"), ("Melbourne", "AU"), ("Perth", "AU"),
    ("Cairns", "AU"), ("Adelaide", "AU"), ("Darwin", "AU"), ("Hobart", "AU"),
    ("Auckland", "NZ"), ("Wellington", "NZ"), ("Christchurch", "NZ"),
    ("Dunedin", "NZ"), ("Papeete", "PF"), ("Nouméa", "NC"), ("Suva", "FJ"),
    ("Rio de Janeiro", "BR"), ("Santos", "BR"), ("Salvador", "BR"),
    ("Buenos Aires", "AR"), ("Ushuaia", "AR"), ("Montevideo", "UY"),
    ("Valparaíso", "CL"), ("Punta Arenas", "CL"), ("Callao", "PE"),
    ("Guayaquil", "EC"), ("Puerto Ayora", "EC"),
)

# The English label is bound straight out of VALUES, tagged @en, so the store
# can use its label index. Written as a FILTER over every label instead — which
# is the obvious way to write it — the query does not finish.
LOOKUP = """
SELECT ?name ?cc ?arLabel WHERE {
  VALUES (?name ?cc) { %(values)s }
  ?city rdfs:label ?name .
  ?city wdt:P17 ?country .
  ?country wdt:P297 ?ccActual .
  FILTER(UCASE(STR(?ccActual)) = STR(?cc))
  ?city rdfs:label ?arLabel .
  FILTER(lang(?arLabel) = "ar")
}
"""

# Second pass, for the dependent territories the first one cannot see. Wikidata
# gives Fort-de-France the country France, not Martinique, so a strict P17 check
# rejects a port that is exactly where it was claimed to be. Walking the
# administrative chain finds Martinique — and its ISO code — one step up.
LOOKUP_TERRITORY = """
SELECT ?name ?cc ?arLabel WHERE {
  VALUES (?name ?cc) { %(values)s }
  ?city rdfs:label ?name .
  ?city wdt:P131* ?area .
  ?area wdt:P297 ?ccActual .
  FILTER(UCASE(STR(?ccActual)) = STR(?cc))
  ?city rdfs:label ?arLabel .
  FILTER(lang(?arLabel) = "ar")
}
"""


def fetch(url: str, params: dict) -> bytes:
    request = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": UA, "Accept": "application/sparql-results+json"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


def ask(query: str) -> list[dict]:
    last = ""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            return json.loads(fetch(WIKIDATA, {"query": query, "format": "json"}))["results"][
                "bindings"
            ]
        except (json.JSONDecodeError, OSError) as error:
            last = str(error)
            print(f"  attempt {attempt}/{ATTEMPTS} failed ({error}); retrying…")
            time.sleep(5 * attempt)
    raise SystemExit(f"Wikidata did not answer after {ATTEMPTS} attempts: {last}")


def plain_name(label: str) -> str:
    """Drop the qualifier Wikidata appends to disambiguate a label.

    Its Arabic for Nagasaki is "ناغاساكي، ناغاساكي" — the city and then the
    prefecture — which the port template turns into "ميناء ناغاساكي، ناغاساكي".
    The country is already its own column here, so the qualifier is noise.
    """
    for separator in ("، ", ", "):
        if separator in label:
            return label.split(separator)[0].strip()
    return label


def slug(city: str, cc: str) -> str:
    """A stable code for the row. Latin-folded, because the model's key should
    not depend on whether anyone can type ș."""
    plain = unicodedata.normalize("NFD", city)
    plain = "".join(ch for ch in plain if unicodedata.category(ch) != "Mn")
    plain = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
    return f"{plain}-{cc.lower()}"


def existing_rows() -> dict[str, dict[str, str]]:
    if not OUT.exists():
        return {}
    with OUT.open(encoding="utf-8", newline="") as handle:
        return {row["code"]: row for row in csv.DictReader(handle)}


def main() -> int:
    existing = existing_rows()
    print(f"ports.csv currently holds {len(existing)} rows")

    # A city already in the catalogue is already verified, and its hand-written
    # name is better than anything built from a template.
    by_city = {(row["city_en"], row["cc"]): row for row in existing.values()}

    # Country names come from the airport catalogue, which covers 233 of them
    # and is where the house spelling lives. The cruise search groups its ports
    # by this string, so "السعودية" here and "المملكة العربية السعودية" there
    # would list one country twice.
    countries = {row["cc"]: (row["country_en"], row["country_ar"]) for row in existing.values()}
    airports = HERE.parent.parent / "airports" / "data" / "airports.csv"
    with airports.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            countries.setdefault(row["cc"], (row["country_en"], row["country_ar"]))

    wanted = list(dict.fromkeys(CANDIDATES))
    todo = [pair for pair in wanted if pair not in by_city]
    print(f"{len(wanted)} candidates, {len(wanted) - len(todo)} already in the catalogue")

    def verify(query: str, pairs: list[tuple[str, str]]) -> dict[tuple[str, str], str]:
        found: dict[tuple[str, str], str] = {}
        for start in range(0, len(pairs), CHUNK):
            chunk = pairs[start : start + CHUNK]
            values = " ".join(f'("{name}"@en "{cc}")' for name, cc in chunk if '"' not in name)
            for binding in ask(query % {"values": values}):
                key = (binding["name"]["value"], binding["cc"]["value"])
                found.setdefault(key, plain_name(binding["arLabel"]["value"].strip()))
            print(f"  {min(start + CHUNK, len(pairs))}/{len(pairs)}")
        return found

    print("verifying the rest against Wikidata…")
    verified = verify(LOOKUP, todo)

    unconfirmed = [pair for pair in todo if pair not in verified]
    if unconfirmed:
        print(f"checking {len(unconfirmed)} more against the territory they sit in…")
        verified |= verify(LOOKUP_TERRITORY, unconfirmed)

    rows = list(existing.values())
    added, dropped = [], []
    for name, cc in todo:
        arabic = verified.get((name, cc))
        if not arabic:
            dropped.append(f"{name} ({cc})")
            continue
        country_en, country_ar = countries.get(cc, ("", ""))
        if not country_en:
            dropped.append(f"{name} ({cc}) — no country name in the catalogue yet")
            continue
        code = slug(name, cc)
        rows.append(
            dict(
                zip(
                    FIELDS,
                    (
                        code,
                        f"Port of {name}",
                        f"ميناء {arabic}",
                        name,
                        arabic,
                        country_en,
                        country_ar,
                        cc,
                    ),
                    strict=True,
                )
            )
        )
        added.append(f"{name} ({cc})")

    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        seen.setdefault(row["code"], row)
    rows = [seen[code] for code in sorted(seen)]

    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nwrote {len(rows)} ports across {len({r['cc'] for r in rows})} countries")
    print(f"  added {len(added)}")
    if dropped:
        print(f"  dropped {len(dropped)} Wikidata would not confirm:")
        for item in dropped:
            print(f"    {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

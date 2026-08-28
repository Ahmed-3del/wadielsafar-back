import pytest
from rest_framework.test import APIClient

from apps.airports.models import Airport
from apps.airports.tests.factories import AirportFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


@pytest.fixture
def clean_airports():
    """The catalogue ships in a data migration, so it is already in the test
    database. Tests that count rows need to start from empty."""
    Airport.objects.all().delete()


def codes(response):
    return [row["iata_code"] for row in response.data["results"]]


def test_public_list_hides_switched_off_airports(clean_airports):
    AirportFactory(is_active=True)
    AirportFactory(is_active=False)

    response = APIClient().get("/api/v1/airports/")

    assert response.status_code == 200
    assert response.data["count"] == 1


def test_content_manager_still_sees_what_they_switched_off(clean_airports):
    AirportFactory(is_active=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    assert client.get("/api/v1/airports/").data["count"] == 1


def test_public_cannot_create_an_airport(clean_airports):
    response = APIClient().post(
        "/api/v1/airports/",
        {
            "iata_code": "ZZZ",
            "name_ar": "مطار",
            "name_en": "Airport",
            "city_ar": "مدينة",
            "city_en": "City",
            "country_ar": "دولة",
            "country_en": "Country",
        },
    )

    assert response.status_code in (401, 403)
    assert Airport.objects.count() == 0


def test_editor_can_create_an_airport(clean_airports):
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = client.post(
        "/api/v1/airports/",
        {
            "iata_code": "zzz",
            "name_ar": "مطار تجريبي",
            "name_en": "Test Airport",
            "city_ar": "مدينة",
            "city_en": "City",
            "country_ar": "دولة",
            "country_en": "Country",
            "country_code": "xx",
        },
    )

    assert response.status_code == 201, response.data
    airport = Airport.objects.get()
    # Lowercase in, normalized on save — a code pasted from a form or an import
    # should not create a second, differently-cased row.
    assert airport.iata_code == "ZZZ"
    assert airport.country_code == "XX"


def test_the_shipped_catalogue_is_there():
    """The picker is useless without it, so its absence should fail loudly."""
    response = APIClient().get("/api/v1/airports/?search=JED")

    assert response.status_code == 200
    assert codes(response)[0] == "JED"


def test_an_exact_code_wins_over_a_name_that_contains_it(clean_airports):
    AirportFactory(iata_code="AAA", city_en="Somewhere", name_en="Dammam Field")
    AirportFactory(iata_code="DMM", city_en="Dammam", name_en="King Fahd")

    assert codes(APIClient().get("/api/v1/airports/?search=DMM"))[0] == "DMM"


def test_a_city_prefix_beats_a_city_that_merely_contains_the_term(clean_airports):
    AirportFactory(iata_code="AAA", city_en="Port London")
    AirportFactory(iata_code="BBB", city_en="London")

    assert codes(APIClient().get("/api/v1/airports/?search=Lond")) == ["BBB", "AAA"]


def test_arabic_search_finds_the_arabic_city(clean_airports):
    AirportFactory(iata_code="AAA", city_ar="الرياض", city_en="Riyadh")
    AirportFactory(iata_code="BBB", city_ar="جدة", city_en="Jeddah")

    assert codes(APIClient().get("/api/v1/airports/?search=الرياض")) == ["AAA"]


def test_search_matches_the_country_too(clean_airports):
    AirportFactory(iata_code="AAA", country_en="Malaysia", country_ar="ماليزيا")
    AirportFactory(iata_code="BBB", country_en="Thailand", country_ar="تايلاند")

    assert codes(APIClient().get("/api/v1/airports/?search=ماليزيا")) == ["AAA"]


def test_popular_airports_lead_the_unsearched_list(clean_airports):
    AirportFactory(iata_code="AAA", is_popular=False, order=1)
    AirportFactory(iata_code="BBB", is_popular=True, order=9)

    assert codes(APIClient().get("/api/v1/airports/"))[0] == "BBB"


def test_the_picker_can_ask_for_only_the_popular_ones(clean_airports):
    AirportFactory(iata_code="AAA", is_popular=False)
    AirportFactory(iata_code="BBB", is_popular=True)

    response = APIClient().get("/api/v1/airports/?is_popular=true")

    assert codes(response) == ["BBB"]


def test_two_codes_cannot_share_a_row(clean_airports):
    AirportFactory(iata_code="AAA")
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = client.post(
        "/api/v1/airports/",
        {
            "iata_code": "AAA",
            "name_ar": "مطار",
            "name_en": "Airport",
            "city_ar": "مدينة",
            "city_en": "City",
            "country_ar": "دولة",
            "country_en": "Country",
        },
    )

    assert response.status_code == 400


def test_a_plain_alef_finds_the_hamza_spelling(clean_airports):
    """Nobody reaches for إ on a phone keyboard when اسطنبول will do."""
    AirportFactory(iata_code="IST", city_ar="إسطنبول", city_en="Istanbul")

    assert codes(APIClient().get("/api/v1/airports/?search=اسطنبول")) == ["IST"]


def test_ta_marbuta_and_ha_are_the_same_letter_to_a_searcher(clean_airports):
    AirportFactory(iata_code="JED", city_ar="جدة", city_en="Jeddah")

    assert codes(APIClient().get("/api/v1/airports/?search=جده")) == ["JED"]


def test_alef_maqsura_and_ya_match_each_other(clean_airports):
    AirportFactory(iata_code="DXB", city_ar="دبي", city_en="Dubai")

    assert codes(APIClient().get("/api/v1/airports/?search=دبى")) == ["DXB"]


def test_tashkeel_does_not_break_a_match(clean_airports):
    AirportFactory(iata_code="AMM", city_ar="عمّان", city_en="Amman")

    assert codes(APIClient().get("/api/v1/airports/?search=عمان")) == ["AMM"]


def test_folded_arabic_reaches_the_airport_name_and_country_too(clean_airports):
    AirportFactory(iata_code="AAA", name_ar="مطار الملك عبدالعزيز", country_ar="السعودية")
    AirportFactory(iata_code="BBB", name_ar="مطار حمد", country_ar="قطر")

    assert codes(APIClient().get("/api/v1/airports/?search=عبدالعزيز")) == ["AAA"]


def test_saving_refreshes_the_folded_columns(clean_airports):
    airport = AirportFactory(iata_code="AAA", city_ar="جدة")
    airport.city_ar = "إسطنبول"
    airport.save()

    assert codes(APIClient().get("/api/v1/airports/?search=اسطنبول")) == ["AAA"]
    assert APIClient().get("/api/v1/airports/?search=جده").data["count"] == 0


def test_the_shipped_catalogue_is_searchable_in_loose_arabic():
    """The migration backfills the folded columns; without it this is empty."""
    response = APIClient().get("/api/v1/airports/?search=اسطنبول")

    assert codes(response)[0] == "IST"

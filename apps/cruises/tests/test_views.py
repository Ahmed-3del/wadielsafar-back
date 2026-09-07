import pytest
from rest_framework.test import APIClient

from apps.cruises.tests.factories import (
    CruiseFactory,
    CruiseItineraryFactory,
    CruisePortFactory,
)
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_public_list_hides_inactive_cruises():
    CruiseFactory(is_active=True)
    CruiseFactory(is_active=False)
    response = APIClient().get("/api/v1/cruises/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_detail_includes_itinerary():
    cruise = CruiseFactory()
    CruiseItineraryFactory(cruise=cruise, day_number=1, port_en="Jeddah")
    CruiseItineraryFactory(cruise=cruise, day_number=2, port_en="Aqaba")

    response = APIClient().get(f"/api/v1/cruises/{cruise.slug}/")
    assert response.status_code == 200
    assert [item["port_en"] for item in response.data["itinerary"]] == ["Jeddah", "Aqaba"]


def test_featured_action_returns_only_featured():
    CruiseFactory(is_featured=True)
    CruiseFactory(is_featured=False)
    response = APIClient().get("/api/v1/cruises/featured/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_public_cannot_write():
    response = APIClient().post("/api/v1/cruises/", {"title_en": "x"})
    assert response.status_code in (401, 403)


def test_staff_can_create_cruise():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    response = client.post(
        "/api/v1/cruises/",
        {
            "title_ar": "رحلة البحر الأحمر",
            "title_en": "Red Sea Cruise",
            "duration_nights": 7,
            "price_from": "6200.00",
        },
    )
    assert response.status_code == 201, response.data


def test_filter_by_nights():
    CruiseFactory(duration_nights=3)
    CruiseFactory(duration_nights=10)
    response = APIClient().get("/api/v1/cruises/?nights_min=5")
    assert response.data["count"] == 1


def test_depart_after_filters_by_sail_date(tmp_path):
    """Cruises sell on dates, so the homepage's single date box means
    'sailing on or after this'."""
    from datetime import date

    CruiseFactory(departure_date=date(2026, 3, 1), is_active=True)
    CruiseFactory(departure_date=date(2026, 9, 1), is_active=True)
    CruiseFactory(departure_date=None, is_active=True)

    client = APIClient()
    response = client.get("/api/v1/cruises/", {"depart_after": "2026-06-01"})

    assert response.status_code == 200
    dates = [row["departure_date"] for row in response.data["results"]]
    assert dates == ["2026-09-01"]


# --------------------------------------------------------------- cruise ports


def test_public_sees_only_active_ports():
    CruisePortFactory(is_active=True)
    CruisePortFactory(is_active=False)

    assert APIClient().get("/api/v1/cruises/ports/").data["count"] == 1


def test_ports_route_is_not_swallowed_by_the_cruise_detail_route():
    """Both live under /cruises/. Registered the other way round, "ports" would
    be read as a cruise slug and answer 404."""
    response = APIClient().get("/api/v1/cruises/ports/")

    assert response.status_code == 200


def test_port_search_matches_an_unpointed_arabic_spelling():
    """Someone hunting for إسطنبول types "اسطنبول"; matching the stored spelling
    literally would find nothing on an Arabic-first site."""
    CruisePortFactory(city_ar="إسطنبول", city_en="Istanbul", name_ar="ميناء غلطة")

    response = APIClient().get("/api/v1/cruises/ports/", {"search": "اسطنبول"})

    assert response.data["count"] == 1


def test_filter_cruises_by_departure_country():
    """The homepage asks for a country first, and that answer alone has to
    filter — the port is the second, optional half."""
    emirati = CruisePortFactory(country_code="AE")
    italian = CruisePortFactory(country_code="IT", country_en="Italy", country_ar="إيطاليا")
    CruiseFactory(departure_port=emirati)
    CruiseFactory(departure_port=italian)

    response = APIClient().get("/api/v1/cruises/", {"country": "AE"})

    assert response.data["count"] == 1
    assert response.data["results"][0]["departure_port"]["country_code"] == "AE"


def test_filter_cruises_by_port():
    rashid = CruisePortFactory(code="dubai-port-rashid", country_code="AE")
    zayed = CruisePortFactory(code="abu-dhabi-zayed", country_code="AE")
    CruiseFactory(departure_port=rashid)
    CruiseFactory(departure_port=zayed)

    response = APIClient().get("/api/v1/cruises/", {"country": "AE", "port": "dubai-port-rashid"})

    assert response.data["count"] == 1
    assert response.data["results"][0]["departure_port"]["code"] == "dubai-port-rashid"


def test_a_cruise_with_no_port_survives_the_country_filter():
    """An unlinked sailing is invisible to the country search rather than an
    error — the port link is optional, and the cruise still publishes."""
    CruiseFactory(departure_port=None)

    assert APIClient().get("/api/v1/cruises/", {"country": "AE"}).data["count"] == 0
    assert APIClient().get("/api/v1/cruises/").data["count"] == 1


def test_the_port_picker_can_load_more_than_the_default_page_cap():
    """The cruise search builds its country list out of the ports it was sent,
    so the hundred-row cap did not shorten a list — it hid countries."""
    for index in range(120):
        CruisePortFactory(code=f"port-{index}")

    response = APIClient().get("/api/v1/cruises/ports/?page_size=500")

    assert response.status_code == 200
    assert len(response.data["results"]) == 120


def test_the_port_catalogue_reaches_past_the_places_already_sailed():
    """It shipped with 105 ports across 54 countries, so most of the Caribbean,
    Alaska and the Baltic could not be chosen at all."""
    from apps.cruises.data.catalogue import PORTS

    assert len(PORTS) > 250
    assert len({row[7] for row in PORTS}) > 90


def test_an_accent_nobody_types_still_finds_the_port():
    CruisePortFactory(code="kusadasi", city_en="Kuşadası", city_ar="كوش أداسي")

    response = APIClient().get("/api/v1/cruises/ports/?search=kusadasi")

    assert [row["code"] for row in response.data["results"]] == ["kusadasi"]

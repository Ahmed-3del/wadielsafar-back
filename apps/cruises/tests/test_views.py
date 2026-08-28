import pytest
from rest_framework.test import APIClient

from apps.cruises.tests.factories import CruiseFactory, CruiseItineraryFactory
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

import pytest
from rest_framework.test import APIClient

from apps.flights.tests.factories import FlightDealFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_public_list_only_returns_active_deals():
    FlightDealFactory(is_active=True)
    FlightDealFactory(is_active=False)
    client = APIClient()
    response = client.get("/api/v1/flights/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_retrieve_by_slug():
    deal = FlightDealFactory(title_en="Riyadh to Cairo")
    client = APIClient()
    response = client.get(f"/api/v1/flights/{deal.slug}/")
    assert response.status_code == 200
    assert response.data["slug"] == "riyadh-to-cairo"


def test_featured_action_returns_unpaginated_array():
    FlightDealFactory(is_featured=True)
    FlightDealFactory(is_featured=False)
    client = APIClient()
    response = client.get("/api/v1/flights/featured/", {"limit": 6})
    assert response.status_code == 200
    assert len(response.data) == 1


def test_filter_by_route_and_price():
    FlightDealFactory(origin_airport_code="RUH", destination_airport_code="DXB", price_from="900")
    FlightDealFactory(origin_airport_code="JED", destination_airport_code="IST", price_from="2500")
    client = APIClient()

    by_origin = client.get("/api/v1/flights/", {"origin_airport_code": "jed"})
    assert by_origin.data["count"] == 1

    by_price = client.get("/api/v1/flights/", {"price_max": "1000"})
    assert by_price.data["count"] == 1


def test_filter_by_cabin_class_and_trip_type():
    FlightDealFactory(cabin_class="BUSINESS", trip_type="ONE_WAY")
    FlightDealFactory(cabin_class="ECONOMY", trip_type="ROUND_TRIP")
    client = APIClient()
    assert client.get("/api/v1/flights/", {"cabin_class": "BUSINESS"}).data["count"] == 1
    assert client.get("/api/v1/flights/", {"trip_type": "ROUND_TRIP"}).data["count"] == 1


def test_public_cannot_create_a_deal():
    client = APIClient()
    response = client.post("/api/v1/flights/", {"title_en": "Nope"})
    assert response.status_code == 401


def test_content_manager_can_create_a_deal():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    response = client.post(
        "/api/v1/flights/",
        {
            "title_ar": "الرياض إلى دبي",
            "title_en": "Riyadh to Dubai",
            "origin_city_ar": "الرياض",
            "origin_city_en": "Riyadh",
            "origin_airport_code": "ruh",
            "destination_city_ar": "دبي",
            "destination_city_en": "Dubai",
            "destination_airport_code": "dxb",
            "trip_type": "ONE_WAY",
            "price_from": "1200.00",
        },
    )
    assert response.status_code == 201
    assert response.data["origin_airport_code"] == "RUH"
    assert response.data["slug"] == "riyadh-to-dubai"

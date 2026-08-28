import pytest
from rest_framework.test import APIClient

from apps.hotels.tests.factories import HotelAmenityFactory, HotelFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_public_list_only_returns_active_hotels():
    HotelFactory(is_active=True)
    HotelFactory(is_active=False)
    client = APIClient()
    response = client.get("/api/v1/hotels/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_retrieve_by_slug_includes_nested_destination_and_amenities():
    hotel = HotelFactory(name_en="Sea View Hotel", amenities=[HotelAmenityFactory(name_en="Spa")])
    client = APIClient()
    response = client.get(f"/api/v1/hotels/{hotel.slug}/")
    assert response.status_code == 200
    assert response.data["destination"]["slug"] == hotel.destination.slug
    assert response.data["amenities"][0]["name_en"] == "Spa"


def test_amenities_endpoint_lists_amenities():
    HotelAmenityFactory()
    client = APIClient()
    response = client.get("/api/v1/hotels/amenities/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_featured_action_returns_unpaginated_array():
    HotelFactory(is_featured=True)
    HotelFactory(is_featured=False)
    client = APIClient()
    response = client.get("/api/v1/hotels/featured/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_filters_by_destination_star_rating_and_price():
    cheap = HotelFactory(star_rating=3, price_per_night_from="300")
    HotelFactory(star_rating=5, price_per_night_from="1500")
    client = APIClient()

    assert client.get("/api/v1/hotels/", {"star_rating": 5}).data["count"] == 1
    assert client.get("/api/v1/hotels/", {"star_rating_min": 4}).data["count"] == 1
    assert client.get("/api/v1/hotels/", {"price_max": "500"}).data["count"] == 1
    assert client.get("/api/v1/hotels/", {"destination": cheap.destination.slug}).data["count"] == 1


def test_public_cannot_create_a_hotel():
    client = APIClient()
    response = client.post("/api/v1/hotels/", {"name_en": "Nope"})
    assert response.status_code == 401


def test_content_manager_can_create_a_hotel_with_amenity_ids():
    destination = HotelFactory().destination
    amenity = HotelAmenityFactory()
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.ADMIN))
    response = client.post(
        "/api/v1/hotels/",
        {
            "name_ar": "فندق البحر",
            "name_en": "Sea Hotel",
            "destination_id": destination.id,
            "amenity_ids": [amenity.id],
            "star_rating": 4,
            "price_per_night_from": "820.00",
            "check_in_time": "15:00:00",
        },
    )
    assert response.status_code == 201
    assert response.data["slug"] == "sea-hotel"
    assert response.data["amenities"][0]["id"] == amenity.id
    assert response.data["check_in_time"] == "15:00:00"

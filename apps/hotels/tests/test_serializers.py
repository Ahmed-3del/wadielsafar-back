import pytest

from apps.hotels.serializers import HotelSerializer
from apps.hotels.tests.factories import HotelAmenityFactory, HotelFactory

pytestmark = pytest.mark.django_db


def test_relations_serialize_nested_on_read():
    hotel = HotelFactory(amenities=[HotelAmenityFactory(name_en="Pool")])
    data = HotelSerializer(hotel).data

    assert data["destination"]["id"] == hotel.destination_id
    assert [amenity["name_en"] for amenity in data["amenities"]] == ["Pool"]
    assert "destination_id" not in data
    assert "amenity_ids" not in data


def test_write_uses_flat_ids():
    destination = HotelFactory().destination
    amenity = HotelAmenityFactory()
    serializer = HotelSerializer(
        data={
            "name_ar": "فندق",
            "name_en": "Test Hotel",
            "destination_id": destination.id,
            "amenity_ids": [amenity.id],
            "star_rating": 4,
            "price_per_night_from": "500.00",
        }
    )
    assert serializer.is_valid(), serializer.errors
    hotel = serializer.save()
    assert hotel.destination == destination
    assert list(hotel.amenities.all()) == [amenity]


@pytest.mark.parametrize("rating", [0, 6, -1])
def test_star_rating_outside_one_to_five_is_rejected(rating):
    destination = HotelFactory().destination
    serializer = HotelSerializer(
        data={
            "name_ar": "فندق",
            "name_en": "Bad Rating Hotel",
            "destination_id": destination.id,
            "star_rating": rating,
            "price_per_night_from": "500.00",
        }
    )
    assert not serializer.is_valid()
    assert "star_rating" in serializer.errors


@pytest.mark.parametrize("rating", [1, 3, 5])
def test_star_rating_inside_one_to_five_is_accepted(rating):
    destination = HotelFactory().destination
    serializer = HotelSerializer(
        data={
            "name_ar": "فندق",
            "name_en": f"Hotel {rating}",
            "destination_id": destination.id,
            "star_rating": rating,
            "price_per_night_from": "500.00",
        }
    )
    assert serializer.is_valid(), serializer.errors

import pytest
from django.core.exceptions import ValidationError

from apps.hotels.models import Hotel
from apps.hotels.tests.factories import HotelAmenityFactory, HotelFactory

pytestmark = pytest.mark.django_db


def test_slug_is_generated_from_english_name():
    hotel = HotelFactory(name_en="Ritz Carlton Riyadh")
    assert hotel.slug == "ritz-carlton-riyadh"


def test_amenity_slug_is_generated_from_english_name():
    amenity = HotelAmenityFactory(name_en="Free WiFi")
    assert amenity.slug == "free-wifi"


def test_star_rating_above_five_fails_model_validation():
    hotel = HotelFactory.build(star_rating=6, destination=HotelFactory().destination)
    with pytest.raises(ValidationError):
        hotel.full_clean()


def test_amenities_relate_both_ways():
    wifi = HotelAmenityFactory(name_en="WiFi")
    hotel = HotelFactory(amenities=[wifi])
    assert list(hotel.amenities.all()) == [wifi]
    assert list(wifi.hotels.all()) == [hotel]


def test_default_ordering_is_featured_then_stars_then_name():
    HotelFactory(name_en="Cheap Inn", star_rating=3, is_featured=False)
    HotelFactory(name_en="Grand Palace", star_rating=4, is_featured=True)
    HotelFactory(name_en="Royal Suites", star_rating=5, is_featured=True)

    assert [h.name_en for h in Hotel.objects.all()] == [
        "Royal Suites",
        "Grand Palace",
        "Cheap Inn",
    ]

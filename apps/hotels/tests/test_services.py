import pytest

from apps.hotels.services import HotelService
from apps.hotels.tests.factories import HotelFactory

pytestmark = pytest.mark.django_db


def test_get_featured_only_returns_active_featured_hotels():
    HotelFactory(is_featured=True, is_active=True)
    HotelFactory(is_featured=False, is_active=True)
    HotelFactory(is_featured=True, is_active=False)

    assert len(HotelService.get_featured(limit=10)) == 1


def test_get_featured_orders_by_star_rating_and_honours_limit():
    HotelFactory(is_featured=True, star_rating=3)
    HotelFactory(is_featured=True, star_rating=5)
    HotelFactory(is_featured=True, star_rating=4)

    featured = list(HotelService.get_featured(limit=2))

    assert [hotel.star_rating for hotel in featured] == [5, 4]

import pytest

from apps.bookings.tests.factories import BookingFactory

pytestmark = pytest.mark.django_db


def test_booking_str_returns_name():
    obj = BookingFactory(name="Sample Booking")
    assert str(obj) == "Sample Booking"

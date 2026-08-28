import pytest

from apps.bookings.serializers import BookingSerializer
from apps.bookings.tests.factories import BookingFactory

pytestmark = pytest.mark.django_db


def test_booking_serializer_includes_name():
    obj = BookingFactory(name="Sample Booking")
    data = BookingSerializer(obj).data
    assert data["name"] == "Sample Booking"

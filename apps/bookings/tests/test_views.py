import pytest
from rest_framework.test import APIClient

from apps.bookings.tests.factories import BookingFactory
from apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_list_requires_authentication():
    BookingFactory()
    client = APIClient()
    response = client.get("/api/v1/bookings/")
    assert response.status_code == 401


def test_authenticated_staff_can_list():
    BookingFactory()
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/bookings/")
    assert response.status_code == 200
    assert response.data["count"] == 1

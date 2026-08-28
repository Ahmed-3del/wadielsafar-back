import pytest

from apps.services.serializers import ServiceSerializer
from apps.services.tests.factories import ServiceFactory

pytestmark = pytest.mark.django_db


def test_service_serializer_exposes_contract_fields():
    service = ServiceFactory(name_en="Hotel Booking", icon="hotel", order=3)
    data = ServiceSerializer(service).data

    assert data["name_en"] == "Hotel Booking"
    assert data["icon"] == "hotel"
    assert data["order"] == 3
    assert data["slug"] == "hotel-booking"
    assert data["is_active"] is True


def test_slug_is_read_only():
    serializer = ServiceSerializer(
        data={"name_ar": "طيران", "name_en": "Flights", "slug": "client-supplied"}
    )
    assert serializer.is_valid(), serializer.errors
    assert "slug" not in serializer.validated_data

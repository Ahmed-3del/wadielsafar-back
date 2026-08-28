import datetime
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.offers.serializers import OfferSerializer
from apps.offers.tests.factories import OfferFactory

pytestmark = pytest.mark.django_db

TODAY = timezone.localdate()


def _payload(**overrides):
    data = {
        "title_ar": "عرض الصيف",
        "title_en": "Summer Sale",
        "service_type": "PACKAGE",
        "price_before": "1000.00",
        "price_after": "750.00",
        "starts_at": str(TODAY),
        "ends_at": str(TODAY + datetime.timedelta(days=5)),
    }
    data.update(overrides)
    return data


def test_computed_fields_are_exposed_read_only():
    offer = OfferFactory(
        starts_at=TODAY - datetime.timedelta(days=1),
        ends_at=TODAY + datetime.timedelta(days=1),
        price_before=Decimal("1000.00"),
        price_after=Decimal("600.00"),
    )
    data = OfferSerializer(offer).data

    assert data["status"] == "ACTIVE"
    assert data["discount_percentage"] == 40


def test_status_and_discount_cannot_be_written():
    serializer = OfferSerializer(data=_payload(status="ACTIVE", discount_percentage=99))
    assert serializer.is_valid(), serializer.errors
    assert "status" not in serializer.validated_data
    assert "discount_percentage" not in serializer.validated_data


def test_end_date_before_start_date_is_rejected():
    serializer = OfferSerializer(
        data=_payload(starts_at=str(TODAY), ends_at=str(TODAY - datetime.timedelta(days=1)))
    )
    assert not serializer.is_valid()
    assert "ends_at" in serializer.errors


def test_discounted_price_above_original_price_is_rejected():
    serializer = OfferSerializer(data=_payload(price_before="500.00", price_after="900.00"))
    assert not serializer.is_valid()
    assert "price_after" in serializer.errors


def test_equal_prices_are_accepted():
    serializer = OfferSerializer(data=_payload(price_before="500.00", price_after="500.00"))
    assert serializer.is_valid(), serializer.errors


def test_partial_update_validates_against_stored_start_date():
    offer = OfferFactory(starts_at=TODAY, ends_at=TODAY + datetime.timedelta(days=5))
    serializer = OfferSerializer(
        offer, data={"ends_at": str(TODAY - datetime.timedelta(days=2))}, partial=True
    )
    assert not serializer.is_valid()
    assert "ends_at" in serializer.errors

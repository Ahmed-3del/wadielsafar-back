from datetime import timedelta

import pytest
from django.utils import timezone

from apps.inquiries.serializers import InquiryCreateSerializer

pytestmark = pytest.mark.django_db


def _valid_payload():
    return {
        "name": "Ali",
        "email": "ali@example.com",
        "phone": "+966500000000",
        "service_type": "FLIGHT",
    }


def test_create_serializer_rejects_invalid_phone():
    serializer = InquiryCreateSerializer(
        data={
            "name": "Ali",
            "email": "ali@example.com",
            "phone": "not-a-phone",
            "service_type": "PACKAGE",
        }
    )
    assert not serializer.is_valid()
    assert "phone" in serializer.errors


def test_create_serializer_accepts_valid_payload():
    serializer = InquiryCreateSerializer(
        data={
            "name": "Ali",
            "email": "ali@example.com",
            "phone": "+966501234567",
            "service_type": "PACKAGE",
        }
    )
    assert serializer.is_valid(), serializer.errors


def test_details_accepts_flat_service_data():
    serializer = InquiryCreateSerializer(
        data={
            **_valid_payload(),
            "details": {"from": "الرياض", "to": "دبي", "pax": 2, "cabin": "ECONOMY"},
        }
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["details"]["pax"] == 2


def test_details_rejects_nested_payloads():
    serializer = InquiryCreateSerializer(
        data={**_valid_payload(), "details": {"passengers": [{"name": "x"}]}}
    )
    assert not serializer.is_valid()
    assert "details" in serializer.errors


def test_details_rejects_oversized_payloads():
    serializer = InquiryCreateSerializer(
        data={**_valid_payload(), "details": {f"k{i}": "v" for i in range(40)}}
    )
    assert not serializer.is_valid()
    assert "details" in serializer.errors


# ------------------------------------------------------------------- dates


def _payload(**overrides):
    data = {
        "name": "Traveller",
        "email": "traveller@example.com",
        "phone": "+966501234567",
        "service_type": "FLIGHT",
        "message": "Looking for a quote.",
        "source": "WEBSITE",
    }
    data.update(overrides)
    return data


def test_travel_date_cannot_be_in_the_past():
    yesterday = timezone.localdate() - timedelta(days=1)
    serializer = InquiryCreateSerializer(data=_payload(travel_date=yesterday.isoformat()))

    assert not serializer.is_valid()
    assert "travel_date" in serializer.errors


def test_travel_date_today_is_fine():
    serializer = InquiryCreateSerializer(
        data=_payload(travel_date=timezone.localdate().isoformat())
    )

    assert serializer.is_valid(), serializer.errors


def test_return_cannot_come_before_departure():
    depart = timezone.localdate() + timedelta(days=10)
    serializer = InquiryCreateSerializer(
        data=_payload(
            details={
                "depart": depart.isoformat(),
                "return": (depart - timedelta(days=2)).isoformat(),
            }
        )
    )

    assert not serializer.is_valid()
    assert "details" in serializer.errors


def test_returning_the_same_day_is_allowed():
    """A day trip is a real booking."""
    depart = timezone.localdate() + timedelta(days=10)
    serializer = InquiryCreateSerializer(
        data=_payload(details={"depart": depart.isoformat(), "return": depart.isoformat()})
    )

    assert serializer.is_valid(), serializer.errors


def test_check_out_cannot_come_before_check_in():
    check_in = timezone.localdate() + timedelta(days=5)
    serializer = InquiryCreateSerializer(
        data=_payload(
            service_type="HOTEL",
            details={
                "check_in": check_in.isoformat(),
                "check_out": (check_in - timedelta(days=1)).isoformat(),
            },
        )
    )

    assert not serializer.is_valid()
    assert "details" in serializer.errors


def test_a_departure_in_the_past_is_rejected_even_inside_details():
    serializer = InquiryCreateSerializer(
        data=_payload(details={"depart": (timezone.localdate() - timedelta(days=1)).isoformat()})
    )

    assert not serializer.is_valid()
    assert "details" in serializer.errors


def test_details_that_are_not_dates_are_left_alone():
    """`details` is free-form; only the known date keys are policed."""
    serializer = InquiryCreateSerializer(
        data=_payload(details={"from": "الرياض (RUH)", "to": "دبي (DXB)", "cabin_class": "ECONOMY"})
    )

    assert serializer.is_valid(), serializer.errors

import datetime

import pytest

from apps.flights.serializers import FlightDealSerializer
from apps.flights.tests.factories import FlightDealFactory

pytestmark = pytest.mark.django_db


def _payload(**overrides):
    data = {
        "title_ar": "الرياض إلى دبي",
        "title_en": "Riyadh to Dubai",
        "origin_city_ar": "الرياض",
        "origin_city_en": "Riyadh",
        "origin_airport_code": "ruh",
        "destination_city_ar": "دبي",
        "destination_city_en": "Dubai",
        "destination_airport_code": "DXB",
        "trip_type": "ONE_WAY",
        "price_from": "1200.00",
    }
    data.update(overrides)
    return data


def test_iata_codes_are_uppercased_by_the_serializer():
    serializer = FlightDealSerializer(data=_payload())
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["origin_airport_code"] == "RUH"


def test_invalid_iata_code_is_rejected():
    serializer = FlightDealSerializer(data=_payload(origin_airport_code="RU1"))
    assert not serializer.is_valid()
    assert "origin_airport_code" in serializer.errors


def test_return_date_before_departure_date_is_rejected():
    serializer = FlightDealSerializer(
        data=_payload(departure_date="2026-09-10", return_date="2026-09-01")
    )
    assert not serializer.is_valid()
    assert "return_date" in serializer.errors


def test_round_trip_with_departure_date_requires_return_date():
    serializer = FlightDealSerializer(
        data=_payload(trip_type="ROUND_TRIP", departure_date="2026-09-10")
    )
    assert not serializer.is_valid()
    assert "return_date" in serializer.errors


def test_one_way_does_not_require_a_return_date():
    serializer = FlightDealSerializer(
        data=_payload(trip_type="ONE_WAY", departure_date="2026-09-10")
    )
    assert serializer.is_valid(), serializer.errors


def test_partial_update_validates_against_stored_departure_date():
    deal = FlightDealFactory(
        departure_date=datetime.date(2026, 9, 10), return_date=datetime.date(2026, 9, 20)
    )
    serializer = FlightDealSerializer(deal, data={"return_date": "2026-09-01"}, partial=True)
    assert not serializer.is_valid()
    assert "return_date" in serializer.errors


def test_serializer_exposes_contract_fields():
    data = FlightDealSerializer(FlightDealFactory()).data
    for field in (
        "slug",
        "origin_airport_code",
        "destination_airport_code",
        "cabin_class",
        "currency",
        "baggage_allowance_kg",
    ):
        assert field in data
    assert data["currency"] == "SAR"

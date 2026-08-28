import pytest

from apps.flights.tests.factories import FlightDealFactory

pytestmark = pytest.mark.django_db


def test_slug_is_generated_from_english_title():
    deal = FlightDealFactory(title_en="Riyadh to Dubai")
    assert deal.slug == "riyadh-to-dubai"


def test_airport_codes_are_uppercased_on_save():
    deal = FlightDealFactory(origin_airport_code="ruh", destination_airport_code="dxb")
    deal.refresh_from_db()
    assert deal.origin_airport_code == "RUH"
    assert deal.destination_airport_code == "DXB"


def test_default_ordering_puts_featured_first_then_cheapest():
    from apps.flights.models import FlightDeal

    FlightDealFactory(price_from="500.00", is_featured=False)
    FlightDealFactory(price_from="900.00", is_featured=True)
    FlightDealFactory(price_from="800.00", is_featured=True)

    prices = [str(deal.price_from) for deal in FlightDeal.objects.all()]
    assert prices == ["800.00", "900.00", "500.00"]

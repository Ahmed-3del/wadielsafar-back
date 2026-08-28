import pytest

from apps.flights.services import FlightService
from apps.flights.tests.factories import FlightDealFactory

pytestmark = pytest.mark.django_db


def test_get_featured_only_returns_active_featured_deals():
    FlightDealFactory(is_featured=True, is_active=True)
    FlightDealFactory(is_featured=False, is_active=True)
    FlightDealFactory(is_featured=True, is_active=False)

    assert len(FlightService.get_featured(limit=10)) == 1


def test_get_featured_respects_the_limit_and_orders_by_price():
    FlightDealFactory(is_featured=True, price_from="900.00")
    FlightDealFactory(is_featured=True, price_from="400.00")
    FlightDealFactory(is_featured=True, price_from="700.00")

    featured = list(FlightService.get_featured(limit=2))

    assert [str(deal.price_from) for deal in featured] == ["400.00", "700.00"]

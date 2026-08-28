import datetime
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.offers.models import OfferStatusChoices
from apps.offers.services import OfferService
from apps.offers.tests.factories import OfferFactory

pytestmark = pytest.mark.django_db

TODAY = timezone.localdate()


def _days(count):
    return datetime.timedelta(days=count)


def test_status_is_scheduled_before_the_window_opens():
    offer = OfferFactory(starts_at=TODAY + _days(3), ends_at=TODAY + _days(10))
    assert OfferService.compute_status(offer) == OfferStatusChoices.SCHEDULED


def test_status_is_active_on_the_start_date():
    offer = OfferFactory(starts_at=TODAY, ends_at=TODAY + _days(10))
    assert OfferService.compute_status(offer) == OfferStatusChoices.ACTIVE


def test_status_is_active_mid_window():
    offer = OfferFactory(starts_at=TODAY - _days(5), ends_at=TODAY + _days(5))
    assert OfferService.compute_status(offer) == OfferStatusChoices.ACTIVE


def test_status_is_active_on_the_end_date():
    offer = OfferFactory(starts_at=TODAY - _days(10), ends_at=TODAY)
    assert OfferService.compute_status(offer) == OfferStatusChoices.ACTIVE


def test_status_is_expired_after_the_window_closes():
    offer = OfferFactory(starts_at=TODAY - _days(10), ends_at=TODAY - _days(1))
    assert OfferService.compute_status(offer) == OfferStatusChoices.EXPIRED


def test_single_day_window_is_active_today():
    offer = OfferFactory(starts_at=TODAY, ends_at=TODAY)
    assert OfferService.compute_status(offer) == OfferStatusChoices.ACTIVE


def test_discount_percentage_is_computed_from_the_price_pair():
    offer = OfferFactory(price_before=Decimal("1000.00"), price_after=Decimal("750.00"))
    assert OfferService.compute_discount_percentage(offer) == 25


def test_discount_percentage_rounds_to_the_nearest_whole_percent():
    offer = OfferFactory(price_before=Decimal("999.00"), price_after=Decimal("799.00"))
    assert OfferService.compute_discount_percentage(offer) == 20


@pytest.mark.parametrize(
    ("before", "after"),
    [(None, Decimal("750.00")), (Decimal("1000.00"), None), (None, None)],
)
def test_discount_percentage_is_none_when_a_price_is_missing(before, after):
    offer = OfferFactory(price_before=before, price_after=after)
    assert OfferService.compute_discount_percentage(offer) is None


def test_discount_percentage_is_none_for_a_zero_original_price():
    offer = OfferFactory(price_before=Decimal("0.00"), price_after=Decimal("0.00"))
    assert OfferService.compute_discount_percentage(offer) is None


def test_get_active_returns_only_active_offers_covering_today():
    covering = OfferFactory(starts_at=TODAY - _days(1), ends_at=TODAY + _days(1))
    OfferFactory(starts_at=TODAY + _days(1), ends_at=TODAY + _days(5))
    OfferFactory(starts_at=TODAY - _days(5), ends_at=TODAY - _days(1))
    OfferFactory(starts_at=TODAY, ends_at=TODAY, is_active=False)

    assert [offer.pk for offer in OfferService.get_active(limit=10)] == [covering.pk]


def test_get_active_honours_the_limit():
    for _ in range(3):
        OfferFactory(starts_at=TODAY, ends_at=TODAY + _days(1))
    assert len(OfferService.get_active(limit=2)) == 2

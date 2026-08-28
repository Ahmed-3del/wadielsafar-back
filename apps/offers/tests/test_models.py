import pytest

from apps.offers.models import Offer
from apps.offers.tests.factories import OfferFactory

pytestmark = pytest.mark.django_db


def test_offer_str_returns_english_title():
    assert str(OfferFactory(title_en="Summer Sale")) == "Summer Sale"


def test_slug_is_generated_from_english_title():
    assert OfferFactory(title_en="Summer Sale").slug == "summer-sale"


def test_default_ordering_puts_featured_then_newest_window_first():
    import datetime

    from django.utils import timezone

    today = timezone.localdate()
    OfferFactory(title_en="Old", starts_at=today - datetime.timedelta(days=10))
    OfferFactory(title_en="Recent", starts_at=today)
    OfferFactory(
        title_en="Featured", starts_at=today - datetime.timedelta(days=20), is_featured=True
    )

    assert [offer.title_en for offer in Offer.objects.all()] == ["Featured", "Recent", "Old"]

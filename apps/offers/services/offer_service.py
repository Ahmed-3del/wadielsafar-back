from decimal import ROUND_HALF_UP, Decimal

from django.utils import timezone

from apps.offers.models import Offer, OfferStatusChoices


class OfferService:
    @staticmethod
    def get_active(limit=6):
        today = timezone.localdate()
        return Offer.objects.filter(
            is_active=True, starts_at__lte=today, ends_at__gte=today
        ).order_by("-is_featured", "-starts_at")[:limit]

    @staticmethod
    def compute_status(offer):
        today = timezone.localdate()
        if offer.starts_at > today:
            return OfferStatusChoices.SCHEDULED
        if offer.ends_at < today:
            return OfferStatusChoices.EXPIRED
        return OfferStatusChoices.ACTIVE

    @staticmethod
    def compute_discount_percentage(offer):
        """None rather than 0 when either price is missing: an offer may be
        promotional copy only, and 0 would read as "no discount"."""
        if offer.price_before is None or offer.price_after is None:
            return None
        price_before = Decimal(offer.price_before)
        price_after = Decimal(offer.price_after)
        if price_before <= 0:
            return None
        discount = (price_before - price_after) / price_before * 100
        return int(discount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

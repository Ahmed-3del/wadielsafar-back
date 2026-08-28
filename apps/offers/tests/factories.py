import datetime
from decimal import Decimal

import factory
from django.utils import timezone

from apps.offers.models import Offer
from common.constants import ServiceTypeChoices


class OfferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Offer

    title_ar = factory.Sequence(lambda n: f"عرض {n}")
    title_en = factory.Sequence(lambda n: f"Offer {n}")
    service_type = ServiceTypeChoices.PACKAGE
    price_before = Decimal("1000.00")
    price_after = Decimal("750.00")
    starts_at = factory.LazyFunction(lambda: timezone.localdate() - datetime.timedelta(days=1))
    ends_at = factory.LazyFunction(lambda: timezone.localdate() + datetime.timedelta(days=7))
    is_active = True

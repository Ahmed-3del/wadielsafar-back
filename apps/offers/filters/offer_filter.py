import django_filters
from django.utils import timezone

from apps.offers.models import Offer, OfferStatusChoices


class OfferFilter(django_filters.FilterSet):
    # `status` is computed from the validity window, so it filters through
    # date comparisons instead of a stored column.
    status = django_filters.ChoiceFilter(
        choices=OfferStatusChoices.choices, method="filter_by_status"
    )

    class Meta:
        model = Offer
        fields = ("service_type", "is_featured", "status")

    def filter_by_status(self, queryset, name, value):
        today = timezone.localdate()
        if value == OfferStatusChoices.SCHEDULED:
            return queryset.filter(starts_at__gt=today)
        if value == OfferStatusChoices.EXPIRED:
            return queryset.filter(ends_at__lt=today)
        if value == OfferStatusChoices.ACTIVE:
            return queryset.filter(starts_at__lte=today, ends_at__gte=today)
        return queryset

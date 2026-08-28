import django_filters
from django.db.models import Q

from apps.destinations.models import Destination


class DestinationFilter(django_filters.FilterSet):
    # One public `country` parameter over two stored columns. Callers filter by
    # whatever name they are showing the visitor, and an Arabic client should
    # not have to know the English spelling to narrow a list it renders in
    # Arabic.
    country = django_filters.CharFilter(method="filter_country")

    class Meta:
        model = Destination
        fields = ("country", "is_active")

    def filter_country(self, queryset, name, value):
        return queryset.filter(Q(country_ar__iexact=value) | Q(country_en__iexact=value))

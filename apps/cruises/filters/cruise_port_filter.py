import django_filters

from apps.cruises.models import CruisePort


class CruisePortFilter(django_filters.FilterSet):
    class Meta:
        model = CruisePort
        # `country_code` is what the homepage narrows by once a country has
        # been chosen; the rest is for the panel's list.
        fields = ("is_active", "is_popular", "country_code")

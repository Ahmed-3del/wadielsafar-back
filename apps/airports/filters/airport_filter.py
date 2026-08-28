import django_filters

from apps.airports.models import Airport


class AirportFilter(django_filters.FilterSet):
    class Meta:
        model = Airport
        fields = ("is_active", "is_popular", "country_code")

import django_filters

from apps.flights.models import FlightDeal


class FlightDealFilter(django_filters.FilterSet):
    origin_airport_code = django_filters.CharFilter(
        field_name="origin_airport_code", lookup_expr="iexact"
    )
    destination_airport_code = django_filters.CharFilter(
        field_name="destination_airport_code", lookup_expr="iexact"
    )
    price_min = django_filters.NumberFilter(field_name="price_from", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price_from", lookup_expr="lte")

    class Meta:
        model = FlightDeal
        fields = (
            "trip_type",
            "cabin_class",
            "origin_airport_code",
            "destination_airport_code",
            "is_featured",
            "price_min",
            "price_max",
        )

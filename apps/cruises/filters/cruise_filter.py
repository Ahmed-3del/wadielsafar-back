import django_filters

from apps.cruises.models import Cruise


class CruiseFilter(django_filters.FilterSet):
    destination = django_filters.CharFilter(field_name="destination__slug")
    price_min = django_filters.NumberFilter(field_name="price_from", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price_from", lookup_expr="lte")
    nights_min = django_filters.NumberFilter(field_name="duration_nights", lookup_expr="gte")
    nights_max = django_filters.NumberFilter(field_name="duration_nights", lookup_expr="lte")
    # "Sailing on or after this date" — what the homepage widget's single date
    # box actually means.
    depart_after = django_filters.DateFilter(field_name="departure_date", lookup_expr="gte")

    class Meta:
        model = Cruise
        fields = (
            "destination",
            "price_min",
            "price_max",
            "nights_min",
            "nights_max",
            "depart_after",
            "is_featured",
        )

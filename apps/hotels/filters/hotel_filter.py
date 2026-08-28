import django_filters

from apps.hotels.models import Hotel


class HotelFilter(django_filters.FilterSet):
    destination = django_filters.CharFilter(field_name="destination__slug")
    star_rating_min = django_filters.NumberFilter(field_name="star_rating", lookup_expr="gte")
    price_min = django_filters.NumberFilter(field_name="price_per_night_from", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price_per_night_from", lookup_expr="lte")

    class Meta:
        model = Hotel
        fields = (
            "destination",
            "star_rating",
            "star_rating_min",
            "is_featured",
            "price_min",
            "price_max",
        )

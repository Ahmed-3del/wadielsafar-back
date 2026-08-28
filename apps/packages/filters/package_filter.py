import django_filters

from apps.packages.models import Package


class PackageFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__slug")
    destination = django_filters.CharFilter(field_name="destination__slug")
    price_min = django_filters.NumberFilter(field_name="price_from", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price_from", lookup_expr="lte")

    class Meta:
        model = Package
        fields = ("category", "destination", "price_min", "price_max", "is_featured")

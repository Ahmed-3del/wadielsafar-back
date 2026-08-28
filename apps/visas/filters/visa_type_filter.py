import django_filters

from apps.visas.models import VisaType


class VisaTypeFilter(django_filters.FilterSet):
    country = django_filters.NumberFilter(field_name="country_id")

    class Meta:
        model = VisaType
        fields = ("country", "purpose", "is_active")

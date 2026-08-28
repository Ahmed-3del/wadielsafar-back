import django_filters

from apps.services.models import Service


class ServiceFilter(django_filters.FilterSet):
    class Meta:
        model = Service
        fields = ("is_active",)

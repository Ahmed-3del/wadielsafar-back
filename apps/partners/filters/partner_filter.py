import django_filters

from apps.partners.models import Partner


class PartnerFilter(django_filters.FilterSet):
    class Meta:
        model = Partner
        fields = ("is_active",)

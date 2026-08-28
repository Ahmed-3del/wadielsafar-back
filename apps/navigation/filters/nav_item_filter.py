import django_filters

from apps.navigation.models import NavItem


class NavItemFilter(django_filters.FilterSet):
    class Meta:
        model = NavItem
        fields = ("group", "is_active")

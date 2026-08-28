import django_filters

from apps.pages.models import Page


class PageFilter(django_filters.FilterSet):
    class Meta:
        model = Page
        # No filterable fields yet — pages is a Phase 1 scaffold; extend once
        # real business fields land.
        fields = ()

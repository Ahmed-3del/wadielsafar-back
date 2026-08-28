from rest_framework import viewsets

from apps.pages.filters.page_filter import PageFilter
from apps.pages.models import Page
from apps.pages.permissions import PagePermission
from apps.pages.serializers import PageSerializer


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (PagePermission,)
    filterset_class = PageFilter
    search_fields = ("name",)

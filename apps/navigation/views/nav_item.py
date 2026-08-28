from rest_framework import viewsets

from apps.navigation.filters.nav_item_filter import NavItemFilter
from apps.navigation.models import NavItem
from apps.navigation.permissions import NavItemPermission
from apps.navigation.serializers import NavItemSerializer
from common.constants import STAFF_CONTENT_ROLES


class NavItemViewSet(viewsets.ModelViewSet):
    serializer_class = NavItemSerializer
    permission_classes = (NavItemPermission,)
    filterset_class = NavItemFilter
    search_fields = ("label_ar", "label_en", "href")
    ordering_fields = ("group", "order", "label_en")
    # The header asks for the whole set in one request; paging it would mean
    # every page load fetching page two to find out if there is one.
    pagination_class = None

    def get_queryset(self):
        queryset = NavItem.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

from rest_framework import viewsets

from apps.company.permissions import CompanyPermission
from common.constants import STAFF_CONTENT_ROLES


class PublishedViewSet(viewsets.ModelViewSet):
    """Shared base for the footer's three lists.

    All of them behave the same way: the public sees what is switched on, and
    whoever switched something off keeps seeing it. Written once so the three
    cannot drift apart.
    """

    permission_classes = (CompanyPermission,)
    model = None

    def get_queryset(self):
        queryset = self.model.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

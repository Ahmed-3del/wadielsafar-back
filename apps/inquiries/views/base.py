from rest_framework import viewsets

from common.constants import STAFF_CONTENT_ROLES


class ActiveForPublicViewSet(viewsets.ModelViewSet):
    """Shared base for the two tables the contact form reads.

    Both behave the same way: the public form renders whatever is switched on,
    and whoever switched something off keeps seeing it. Written once so the
    two cannot drift apart.
    """

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

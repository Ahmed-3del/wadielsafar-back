from rest_framework import viewsets

from apps.pages.models import PageHero
from apps.pages.permissions import PagePermission
from apps.pages.serializers import PageHeroSerializer
from common.constants import STAFF_CONTENT_ROLES


class PageHeroViewSet(viewsets.ModelViewSet):
    serializer_class = PageHeroSerializer
    permission_classes = (PagePermission,)
    # Looked up by page_key so the site can ask for "the hero for /visas"
    # without first having to discover an opaque id.
    lookup_field = "page_key"

    def get_queryset(self):
        queryset = PageHero.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

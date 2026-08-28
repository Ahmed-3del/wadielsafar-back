from rest_framework import viewsets

from apps.destinations.filters.destination_filter import DestinationFilter
from apps.destinations.models import Destination
from apps.destinations.permissions import DestinationPermission
from apps.destinations.serializers import DestinationSerializer
from common.constants import STAFF_CONTENT_ROLES


class DestinationViewSet(viewsets.ModelViewSet):
    serializer_class = DestinationSerializer
    permission_classes = (DestinationPermission,)
    filterset_class = DestinationFilter
    search_fields = ("name_ar", "name_en", "country_ar", "country_en")
    ordering_fields = ("order", "name_en", "created_at")
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Destination.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

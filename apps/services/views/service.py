from rest_framework import viewsets

from apps.services.filters.service_filter import ServiceFilter
from apps.services.models import Service
from apps.services.permissions import ServicePermission
from apps.services.serializers import ServiceSerializer
from common.constants import STAFF_CONTENT_ROLES


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = (ServicePermission,)
    filterset_class = ServiceFilter
    search_fields = ("name_ar", "name_en", "description_ar", "description_en")
    ordering_fields = ("order", "name_en", "created_at")

    def get_queryset(self):
        queryset = Service.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

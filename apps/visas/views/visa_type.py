from rest_framework import viewsets

from apps.visas.filters.visa_type_filter import VisaTypeFilter
from apps.visas.models import VisaType
from apps.visas.permissions import VisaPermission
from apps.visas.serializers import VisaTypeSerializer
from common.constants import STAFF_CONTENT_ROLES


class VisaTypeViewSet(viewsets.ModelViewSet):
    serializer_class = VisaTypeSerializer
    permission_classes = (VisaPermission,)
    filterset_class = VisaTypeFilter
    search_fields = ("name_ar", "name_en")

    def get_queryset(self):
        queryset = VisaType.objects.select_related("country")
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

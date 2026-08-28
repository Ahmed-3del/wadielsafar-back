from rest_framework import viewsets

from apps.visas.models import VisaCountry
from apps.visas.permissions import VisaPermission
from apps.visas.serializers import VisaCountrySerializer
from common.constants import STAFF_CONTENT_ROLES


class VisaCountryViewSet(viewsets.ModelViewSet):
    serializer_class = VisaCountrySerializer
    permission_classes = (VisaPermission,)
    search_fields = ("name_ar", "name_en")

    def get_queryset(self):
        queryset = VisaCountry.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

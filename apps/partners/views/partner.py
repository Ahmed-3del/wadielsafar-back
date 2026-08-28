from rest_framework import viewsets

from apps.partners.filters.partner_filter import PartnerFilter
from apps.partners.models import Partner
from apps.partners.permissions import PartnerPermission
from apps.partners.serializers import PartnerSerializer
from common.constants import STAFF_CONTENT_ROLES


class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerSerializer
    permission_classes = (PartnerPermission,)
    filterset_class = PartnerFilter
    search_fields = ("name_ar", "name_en")
    ordering_fields = ("order", "name_en", "created_at")

    def get_queryset(self):
        queryset = Partner.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        # A partner switched off is switched off for the public, but has to stay
        # visible to whoever switched it off.
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

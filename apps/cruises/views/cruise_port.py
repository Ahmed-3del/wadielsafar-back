from rest_framework import viewsets

from apps.cruises.filters import CruisePortFilter
from apps.cruises.models import CruisePort
from apps.cruises.permissions import CruisePermission
from apps.cruises.serializers import CruisePortSerializer
from apps.cruises.services import CruisePortSearchService
from common.constants import STAFF_CONTENT_ROLES
from common.imports import BulkImportMixin
from common.imports.columns import CRUISE_PORT_COLUMNS
from common.pagination import ReferenceDataPagination


class CruisePortViewSet(BulkImportMixin, viewsets.ModelViewSet):
    import_columns = CRUISE_PORT_COLUMNS
    import_key = "code"
    serializer_class = CruisePortSerializer
    permission_classes = (CruisePermission,)
    filterset_class = CruisePortFilter
    ordering_fields = ("city_en", "country_en", "order")
    # The picker asks for the whole catalogue in one request and builds its
    # country list out of it, so a page cap would quietly hide countries.
    pagination_class = ReferenceDataPagination

    def get_queryset(self):
        queryset = CruisePort.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        # A port switched off is gone from the pickers, but has to stay visible
        # to whoever switched it off.
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

    def filter_queryset(self, queryset):
        # Ranking last: DRF's ordering backend would otherwise replace the
        # order_by the search service just applied.
        queryset = super().filter_queryset(queryset)
        return CruisePortSearchService.search(queryset, self.request.query_params.get("search", ""))

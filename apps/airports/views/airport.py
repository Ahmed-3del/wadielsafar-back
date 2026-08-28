from rest_framework import viewsets

from apps.airports.filters import AirportFilter
from apps.airports.models import Airport
from apps.airports.permissions import AirportPermission
from apps.airports.serializers import AirportSerializer
from apps.airports.services import AirportSearchService
from common.constants import STAFF_CONTENT_ROLES


class AirportViewSet(viewsets.ModelViewSet):
    serializer_class = AirportSerializer
    permission_classes = (AirportPermission,)
    filterset_class = AirportFilter
    ordering_fields = ("iata_code", "city_en", "order")

    def get_queryset(self):
        queryset = Airport.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        # An airport switched off is gone from the pickers, but has to stay
        # visible to whoever switched it off.
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

    def filter_queryset(self, queryset):
        # Ranking has to come last: DRF's ordering backend would otherwise
        # replace the order_by the search service just applied.
        queryset = super().filter_queryset(queryset)
        return AirportSearchService.search(queryset, self.request.query_params.get("search", ""))

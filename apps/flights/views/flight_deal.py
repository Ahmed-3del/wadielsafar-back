from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.flights.filters.flight_filter import FlightDealFilter
from apps.flights.models import FlightDeal
from apps.flights.permissions import FlightPermission
from apps.flights.serializers import FlightDealSerializer
from apps.flights.services import FlightService
from common.constants import STAFF_CONTENT_ROLES


class FlightDealViewSet(viewsets.ModelViewSet):
    serializer_class = FlightDealSerializer
    permission_classes = (FlightPermission,)
    filterset_class = FlightDealFilter
    search_fields = (
        "title_ar",
        "title_en",
        "origin_city_ar",
        "origin_city_en",
        "destination_city_ar",
        "destination_city_en",
    )
    ordering_fields = ("price_from", "departure_date", "created_at")
    lookup_field = "slug"

    def get_queryset(self):
        queryset = FlightDeal.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=["get"])
    def featured(self, request):
        limit = int(request.query_params.get("limit", 6))
        deals = FlightService.get_featured(limit=limit)
        serializer = FlightDealSerializer(deals, many=True, context={"request": request})
        return Response(serializer.data)

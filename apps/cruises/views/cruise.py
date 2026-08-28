from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cruises.filters.cruise_filter import CruiseFilter
from apps.cruises.models import Cruise
from apps.cruises.permissions import CruisePermission
from apps.cruises.serializers import CruiseDetailSerializer, CruiseSerializer
from apps.cruises.services import CruiseService
from common.constants import STAFF_CONTENT_ROLES


class CruiseViewSet(viewsets.ModelViewSet):
    permission_classes = (CruisePermission,)
    filterset_class = CruiseFilter
    search_fields = ("title_ar", "title_en", "cruise_line_ar", "cruise_line_en")
    ordering_fields = ("price_from", "duration_nights", "created_at")
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Cruise.objects.select_related("destination").prefetch_related("itinerary")
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CruiseDetailSerializer
        return CruiseSerializer

    @action(detail=False, methods=["get"])
    def featured(self, request):
        limit = int(request.query_params.get("limit", 6))
        cruises = CruiseService.get_featured(limit=limit)
        serializer = CruiseSerializer(cruises, many=True, context={"request": request})
        return Response(serializer.data)

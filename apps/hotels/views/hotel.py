from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.hotels.filters.hotel_filter import HotelFilter
from apps.hotels.models import Hotel
from apps.hotels.permissions import HotelPermission
from apps.hotels.serializers import HotelSerializer
from apps.hotels.services import HotelService
from common.constants import STAFF_CONTENT_ROLES


class HotelViewSet(viewsets.ModelViewSet):
    serializer_class = HotelSerializer
    permission_classes = (HotelPermission,)
    filterset_class = HotelFilter
    search_fields = (
        "name_ar",
        "name_en",
        "address_ar",
        "address_en",
        "description_ar",
        "description_en",
    )
    ordering_fields = ("price_per_night_from", "star_rating", "created_at")
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Hotel.objects.select_related("destination").prefetch_related("amenities")
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
        hotels = HotelService.get_featured(limit=limit)
        serializer = HotelSerializer(hotels, many=True, context={"request": request})
        return Response(serializer.data)

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.offers.filters.offer_filter import OfferFilter
from apps.offers.models import Offer
from apps.offers.permissions import OfferPermission
from apps.offers.serializers import OfferSerializer
from apps.offers.services import OfferService
from common.constants import STAFF_CONTENT_ROLES


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = (OfferPermission,)
    filterset_class = OfferFilter
    search_fields = ("title_ar", "title_en", "description_ar", "description_en")
    ordering_fields = ("starts_at", "ends_at", "created_at")
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Offer.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=["get"])
    def active(self, request):
        limit = int(request.query_params.get("limit", 6))
        offers = OfferService.get_active(limit=limit)
        serializer = OfferSerializer(offers, many=True, context={"request": request})
        return Response(serializer.data)

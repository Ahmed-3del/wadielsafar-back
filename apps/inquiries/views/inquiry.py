from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from apps.inquiries.filters.inquiry_filter import InquiryFilter
from apps.inquiries.models import Inquiry
from apps.inquiries.permissions import InquiryAdminPermission
from apps.inquiries.serializers import (
    InquiryCreateSerializer,
    InquirySerializer,
    InquiryStatusUpdateSerializer,
)
from apps.inquiries.services import InquiryService


class InquiryCreateThrottle(AnonRateThrottle):
    scope = "inquiry_create"


class InquiryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Public POST captures leads (the Phase 1 priority); everything else —
    viewing and progressing a lead through its pipeline — is staff-only.
    No delete: inquiries are never destroyed, only closed."""

    queryset = Inquiry.objects.select_related("destination").all()
    filterset_class = InquiryFilter
    search_fields = ("name", "email", "phone")

    def get_serializer_class(self):
        if self.action == "create":
            return InquiryCreateSerializer
        if self.action in ("update", "partial_update"):
            return InquiryStatusUpdateSerializer
        return InquirySerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [InquiryAdminPermission()]

    def get_throttles(self):
        if self.action == "create":
            return [InquiryCreateThrottle()]
        return []

    def perform_create(self, serializer):
        self.instance = InquiryService.create_inquiry(serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = InquirySerializer(self.instance)
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        InquiryService.update_status(serializer.instance, serializer.validated_data["status"])

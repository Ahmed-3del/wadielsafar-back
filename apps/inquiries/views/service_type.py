from apps.inquiries.models import InquiryServiceType
from apps.inquiries.permissions import InquiryFieldPermission
from apps.inquiries.serializers import InquiryServiceTypeSerializer
from apps.inquiries.views.base import ActiveForPublicViewSet


class InquiryServiceTypeViewSet(ActiveForPublicViewSet):
    """The contact form's service list. Read by the public form, written by
    whoever manages content."""

    model = InquiryServiceType
    serializer_class = InquiryServiceTypeSerializer
    permission_classes = (InquiryFieldPermission,)
    filterset_fields = ("is_active",)
    ordering_fields = ("order", "value")

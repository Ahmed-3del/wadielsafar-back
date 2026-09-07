from apps.inquiries.models import InquiryField
from apps.inquiries.permissions import InquiryFieldPermission
from apps.inquiries.serializers import InquiryFieldSerializer
from apps.inquiries.views.base import ActiveForPublicViewSet


class InquiryFieldViewSet(ActiveForPublicViewSet):
    """The contact form's per-service questions.

    Readable by anyone, because the public contact form renders them; writable
    by whoever manages content.
    """

    model = InquiryField
    serializer_class = InquiryFieldSerializer
    permission_classes = (InquiryFieldPermission,)
    filterset_fields = ("service_type", "is_active")
    ordering_fields = ("service_type", "order")

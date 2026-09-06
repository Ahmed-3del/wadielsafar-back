from rest_framework import viewsets

from apps.inquiries.models import InquiryField
from apps.inquiries.permissions import InquiryFieldPermission
from apps.inquiries.serializers import InquiryFieldSerializer
from common.constants import STAFF_CONTENT_ROLES


class InquiryFieldViewSet(viewsets.ModelViewSet):
    """The contact form's per-service questions.

    Readable by anyone, because the public contact form renders them; writable
    by whoever manages content.
    """

    serializer_class = InquiryFieldSerializer
    permission_classes = (InquiryFieldPermission,)
    filterset_fields = ("service_type", "is_active")
    ordering_fields = ("service_type", "order")

    def get_queryset(self):
        queryset = InquiryField.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        # A question switched off is gone from the form, but has to stay
        # visible to whoever switched it off.
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

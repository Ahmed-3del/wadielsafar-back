import logging

from apps.inquiries.models import Inquiry
from apps.integrations.zoho.tasks import sync_inquiry_to_zoho

logger = logging.getLogger(__name__)


class InquiryService:
    @staticmethod
    def create_inquiry(data: dict) -> Inquiry:
        inquiry = Inquiry.objects.create(**data)
        InquiryService._enqueue_zoho_sync(inquiry)
        return inquiry

    @staticmethod
    def update_status(inquiry: Inquiry, status: str) -> Inquiry:
        inquiry.status = status
        inquiry.save(update_fields=["status", "updated_at"])
        return inquiry

    @staticmethod
    def _enqueue_zoho_sync(inquiry: Inquiry) -> None:
        try:
            sync_inquiry_to_zoho.delay(inquiry.pk)
        except Exception:
            # An unreachable broker must not turn a captured lead into a 500.
            # The inquiry row is saved either way and can be re-synced later.
            logger.exception("Could not enqueue the Zoho sync for inquiry %s", inquiry.pk)

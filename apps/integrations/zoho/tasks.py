import logging

from celery import shared_task

from apps.inquiries.models import Inquiry
from apps.integrations.zoho.exceptions import ZohoError
from apps.integrations.zoho.models import ZohoSyncStatusChoices
from apps.integrations.zoho.services import ZohoService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(ZohoError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
)
def sync_inquiry_to_zoho(self, inquiry_id: int):
    inquiry = Inquiry.objects.select_related("destination").filter(pk=inquiry_id).first()
    if inquiry is None:
        logger.warning("Zoho sync skipped: inquiry %s no longer exists.", inquiry_id)
        return None

    sync_log = ZohoService.sync_lead(inquiry, attempt=self.request.retries + 1)
    if sync_log.status == ZohoSyncStatusChoices.FAILED:
        # sync_lead deliberately swallows failures so its callers never
        # break; re-raising here is what drives Celery's retry/backoff.
        raise ZohoError(sync_log.error_message)
    return sync_log.zoho_record_id

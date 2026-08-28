import logging

from apps.integrations.zoho.models import ZohoSyncLog, ZohoSyncStatusChoices
from apps.integrations.zoho.services.zoho_client import ZohoClient

logger = logging.getLogger(__name__)

# Zoho requires Company on a Lead, but website leads are individual
# travelers — a constant records the capture channel instead.
LEAD_COMPANY = "Wadi Al Safar Website"


class ZohoService:
    @staticmethod
    def build_lead_payload(inquiry) -> dict:
        # Zoho's stock Lead module has no service-type or destination field,
        # so both are folded into the description rather than pushed to
        # custom fields that may not exist in the target org.
        description = [f"Service type: {inquiry.get_service_type_display()}"]
        if inquiry.destination_id:
            description.append(f"Destination: {inquiry.destination.name_en}")
        if inquiry.travel_date:
            description.append(f"Travel date: {inquiry.travel_date.isoformat()}")
        if inquiry.message:
            description.extend(["", inquiry.message])

        return {
            "Last_Name": inquiry.name,
            "Email": inquiry.email,
            "Phone": inquiry.phone,
            "Company": LEAD_COMPANY,
            "Lead_Source": inquiry.get_source_display(),
            "Description": "\n".join(description),
        }

    @staticmethod
    def sync_lead(inquiry, attempt: int = 1) -> ZohoSyncLog:
        """Pushes an inquiry to Zoho and records the outcome. Never raises:
        lead capture must succeed even when Zoho is down or unconfigured —
        the caller decides what to do with the returned log."""
        client = ZohoClient()

        if not client.is_configured:
            logger.info("Zoho sync skipped for inquiry %s: credentials not configured.", inquiry.pk)
            return ZohoSyncLog.objects.create(
                inquiry=inquiry,
                status=ZohoSyncStatusChoices.SKIPPED,
                error_message="Zoho credentials are not configured.",
                attempts=0,
            )

        try:
            record_id = client.push_lead(ZohoService.build_lead_payload(inquiry))
        except Exception as exc:
            logger.warning("Zoho lead sync failed for inquiry %s: %s", inquiry.pk, exc)
            return ZohoSyncLog.objects.create(
                inquiry=inquiry,
                status=ZohoSyncStatusChoices.FAILED,
                error_message=str(exc),
                attempts=attempt,
            )

        return ZohoSyncLog.objects.create(
            inquiry=inquiry,
            status=ZohoSyncStatusChoices.SUCCESS,
            zoho_record_id=record_id,
            attempts=attempt,
        )

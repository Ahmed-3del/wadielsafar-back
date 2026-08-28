import datetime
from unittest.mock import patch

import pytest

from apps.destinations.tests.factories import DestinationFactory
from apps.inquiries.tests.factories import InquiryFactory
from apps.integrations.zoho.models import ZohoSyncLog, ZohoSyncStatusChoices
from apps.integrations.zoho.services import ZohoService
from apps.integrations.zoho.services.zoho_service import LEAD_COMPANY
from apps.integrations.zoho.tests.conftest import FakeResponse
from common.constants import InquirySourceChoices, ServiceTypeChoices

pytestmark = pytest.mark.django_db

POST_TARGET = "apps.integrations.zoho.services.zoho_client.requests.post"


def test_build_lead_payload_maps_the_inquiry_to_zoho_lead_fields():
    destination = DestinationFactory(name_en="Istanbul")
    inquiry = InquiryFactory(
        name="Sara",
        email="sara@example.com",
        phone="+966501234567",
        service_type=ServiceTypeChoices.PACKAGE,
        source=InquirySourceChoices.WEBSITE,
        destination=destination,
        travel_date=datetime.date(2026, 10, 1),
        message="Looking for a family trip.",
    )

    payload = ZohoService.build_lead_payload(inquiry)

    assert payload["Last_Name"] == "Sara"
    assert payload["Email"] == "sara@example.com"
    assert payload["Phone"] == "+966501234567"
    assert payload["Company"] == LEAD_COMPANY
    assert payload["Lead_Source"] == "Website"
    assert "Service type: Package" in payload["Description"]
    assert "Destination: Istanbul" in payload["Description"]
    assert "Travel date: 2026-10-01" in payload["Description"]
    assert "Looking for a family trip." in payload["Description"]


def test_sync_lead_records_skipped_and_makes_no_http_call_when_unconfigured(zoho_unconfigured):
    inquiry = InquiryFactory()

    with patch(POST_TARGET) as post:
        sync_log = ZohoService.sync_lead(inquiry)

    post.assert_not_called()
    assert sync_log.status == ZohoSyncStatusChoices.SKIPPED
    assert sync_log.zoho_record_id == ""
    assert sync_log.attempts == 0
    assert "not configured" in sync_log.error_message


def test_sync_lead_records_success_with_the_returned_record_id(
    zoho_configured, token_response, lead_created_response
):
    inquiry = InquiryFactory()

    with patch(POST_TARGET, side_effect=[token_response, lead_created_response]):
        sync_log = ZohoService.sync_lead(inquiry)

    assert sync_log.status == ZohoSyncStatusChoices.SUCCESS
    assert sync_log.zoho_record_id == "3477061000000419001"
    assert sync_log.error_message == ""
    assert sync_log.attempts == 1
    assert list(inquiry.zoho_syncs.all()) == [sync_log]


def test_sync_lead_records_failure_without_raising(zoho_configured, token_response):
    inquiry = InquiryFactory()
    failure = FakeResponse(status_code=502, text="bad gateway")

    with patch(POST_TARGET, side_effect=[token_response, failure]):
        sync_log = ZohoService.sync_lead(inquiry)

    assert sync_log.status == ZohoSyncStatusChoices.FAILED
    assert sync_log.zoho_record_id == ""
    assert "502" in sync_log.error_message


def test_sync_lead_swallows_unexpected_errors(zoho_configured):
    inquiry = InquiryFactory()

    with patch(
        "apps.integrations.zoho.services.zoho_service.ZohoClient.push_lead",
        side_effect=RuntimeError("unexpected"),
    ):
        sync_log = ZohoService.sync_lead(inquiry)

    assert sync_log.status == ZohoSyncStatusChoices.FAILED
    assert "unexpected" in sync_log.error_message


def test_sync_lead_stores_the_attempt_number(zoho_configured, token_response):
    inquiry = InquiryFactory()
    failure = FakeResponse(status_code=500, text="boom")

    with patch(POST_TARGET, side_effect=[token_response, failure]):
        ZohoService.sync_lead(inquiry, attempt=3)

    assert ZohoSyncLog.objects.get(inquiry=inquiry).attempts == 3

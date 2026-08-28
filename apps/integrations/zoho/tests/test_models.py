import pytest

from apps.inquiries.tests.factories import InquiryFactory
from apps.integrations.zoho.models import ZohoSyncLog, ZohoSyncStatusChoices

pytestmark = pytest.mark.django_db


def test_defaults_to_pending_with_no_record_or_error():
    log = ZohoSyncLog.objects.create(inquiry=InquiryFactory())
    assert log.status == ZohoSyncStatusChoices.PENDING
    assert log.zoho_record_id == ""
    assert log.error_message == ""
    assert log.attempts == 0


def test_logs_are_reachable_from_the_inquiry():
    inquiry = InquiryFactory()
    log = ZohoSyncLog.objects.create(inquiry=inquiry, status=ZohoSyncStatusChoices.SUCCESS)
    assert list(inquiry.zoho_syncs.all()) == [log]

from unittest.mock import patch

import pytest
from celery.exceptions import Retry

from apps.inquiries.tests.factories import InquiryFactory
from apps.integrations.zoho.exceptions import ZohoError
from apps.integrations.zoho.models import ZohoSyncLog, ZohoSyncStatusChoices
from apps.integrations.zoho.tasks import sync_inquiry_to_zoho

pytestmark = pytest.mark.django_db

POST_TARGET = "apps.integrations.zoho.services.zoho_client.requests.post"


def test_task_is_configured_with_bounded_exponential_retries():
    assert ZohoError in sync_inquiry_to_zoho.autoretry_for
    assert sync_inquiry_to_zoho.max_retries == 3
    assert sync_inquiry_to_zoho.retry_backoff is True


def test_task_returns_the_zoho_record_id_on_success(
    zoho_configured, token_response, lead_created_response
):
    inquiry = InquiryFactory()

    with patch(POST_TARGET, side_effect=[token_response, lead_created_response]):
        result = sync_inquiry_to_zoho(inquiry.pk)

    assert result == "3477061000000419001"
    assert ZohoSyncLog.objects.get(inquiry=inquiry).status == ZohoSyncStatusChoices.SUCCESS


def test_task_is_a_noop_for_a_deleted_inquiry(zoho_configured):
    with patch(POST_TARGET) as post:
        assert sync_inquiry_to_zoho(999_999) is None
    post.assert_not_called()


def test_task_retries_when_the_sync_is_recorded_as_failed(zoho_configured, token_response):
    from apps.integrations.zoho.tests.conftest import FakeResponse

    inquiry = InquiryFactory()
    failure = FakeResponse(status_code=500, text="boom")

    with patch(POST_TARGET, side_effect=[token_response, failure]):
        with patch.object(sync_inquiry_to_zoho, "retry", side_effect=Retry()) as retry:
            with pytest.raises(Retry):
                sync_inquiry_to_zoho(inquiry.pk)

    retry.assert_called_once()
    assert isinstance(retry.call_args.kwargs["exc"], ZohoError)
    assert ZohoSyncLog.objects.get(inquiry=inquiry).status == ZohoSyncStatusChoices.FAILED


def test_task_does_not_retry_when_zoho_is_unconfigured(zoho_unconfigured):
    inquiry = InquiryFactory()

    with patch.object(sync_inquiry_to_zoho, "retry") as retry:
        assert sync_inquiry_to_zoho(inquiry.pk) == ""

    retry.assert_not_called()
    assert ZohoSyncLog.objects.get(inquiry=inquiry).status == ZohoSyncStatusChoices.SKIPPED

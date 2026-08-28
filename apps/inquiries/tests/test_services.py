from unittest.mock import patch

import pytest

from apps.inquiries.models import Inquiry
from apps.inquiries.services import InquiryService
from apps.inquiries.tests.factories import InquiryFactory
from common.constants import InquiryStatusChoices, ServiceTypeChoices

pytestmark = pytest.mark.django_db

DELAY_TARGET = "apps.inquiries.services.inquiry_service.sync_inquiry_to_zoho.delay"


def test_create_inquiry_persists_row_and_enqueues_the_zoho_sync():
    with patch(DELAY_TARGET) as delay:
        inquiry = InquiryService.create_inquiry(
            {
                "name": "Sara",
                "email": "sara@example.com",
                "phone": "+966501234567",
                "service_type": ServiceTypeChoices.VISA,
            }
        )

    assert Inquiry.objects.filter(pk=inquiry.pk).exists()
    assert inquiry.status == InquiryStatusChoices.NEW
    delay.assert_called_once_with(inquiry.pk)


def test_create_inquiry_survives_an_unreachable_broker():
    with patch(DELAY_TARGET, side_effect=OSError("broker unreachable")):
        inquiry = InquiryService.create_inquiry(
            {
                "name": "Sara",
                "email": "sara@example.com",
                "phone": "+966501234567",
                "service_type": ServiceTypeChoices.FLIGHT,
            }
        )

    assert Inquiry.objects.filter(pk=inquiry.pk).exists()


def test_update_status_changes_and_saves():
    inquiry = InquiryFactory(status=InquiryStatusChoices.NEW)
    updated = InquiryService.update_status(inquiry, InquiryStatusChoices.CONTACTED)
    updated.refresh_from_db()
    assert updated.status == InquiryStatusChoices.CONTACTED

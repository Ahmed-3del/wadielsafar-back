import pytest

from apps.inquiries.tests.factories import InquiryFactory
from common.constants import InquirySourceChoices, InquiryStatusChoices

pytestmark = pytest.mark.django_db


def test_inquiry_defaults_status_new_and_source_website():
    inquiry = InquiryFactory()
    assert inquiry.status == InquiryStatusChoices.NEW
    assert inquiry.source == InquirySourceChoices.WEBSITE


def test_inquiry_destination_is_optional():
    inquiry = InquiryFactory(destination=None)
    assert inquiry.destination is None

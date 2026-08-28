from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.inquiries.tests.factories import InquiryFactory
from apps.users.tests.factories import UserFactory
from common.constants import InquiryStatusChoices, RoleChoices

pytestmark = pytest.mark.django_db


def test_public_can_create_inquiry():
    client = APIClient()
    with patch("apps.inquiries.services.inquiry_service.sync_inquiry_to_zoho.delay") as delay:
        response = client.post(
            "/api/v1/inquiries/",
            {
                "name": "Sara",
                "email": "sara@example.com",
                "phone": "+966501234567",
                "service_type": "PACKAGE",
                "message": "Looking for a Turkey package.",
            },
        )
    assert response.status_code == 201
    assert response.data["status"] == "NEW"
    delay.assert_called_once_with(response.data["id"])


def test_lead_capture_succeeds_when_the_broker_is_unreachable():
    client = APIClient()
    with patch(
        "apps.inquiries.services.inquiry_service.sync_inquiry_to_zoho.delay",
        side_effect=OSError("broker unreachable"),
    ):
        response = client.post(
            "/api/v1/inquiries/",
            {
                "name": "Omar",
                "email": "omar@example.com",
                "phone": "+966501234568",
                "service_type": "FLIGHT",
            },
        )
    assert response.status_code == 201


def test_public_cannot_list_inquiries():
    InquiryFactory()
    client = APIClient()
    response = client.get("/api/v1/inquiries/")
    assert response.status_code == 401


def test_sales_staff_can_list_and_update_status():
    sales = UserFactory(role=RoleChoices.SALES)
    inquiry = InquiryFactory(status=InquiryStatusChoices.NEW)
    client = APIClient()
    client.force_authenticate(user=sales)

    list_response = client.get("/api/v1/inquiries/")
    assert list_response.status_code == 200
    assert list_response.data["count"] == 1

    update_response = client.patch(f"/api/v1/inquiries/{inquiry.pk}/", {"status": "CONTACTED"})
    assert update_response.status_code == 200
    inquiry.refresh_from_db()
    assert inquiry.status == InquiryStatusChoices.CONTACTED

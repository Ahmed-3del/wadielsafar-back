from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.inquiries.models import InquiryField
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


# ------------------------------------------------------- contact form fields


def test_anyone_can_read_the_contact_form_questions():
    """The public contact form renders them, so they cannot be staff-only."""
    InquiryField.objects.create(
        service_type="FLIGHT", key="from", label_ar="من", label_en="From"
    )

    response = APIClient().get("/api/v1/inquiries/fields/")

    assert response.status_code == 200
    assert response.data["count"] == 1


def test_the_public_cannot_change_what_the_form_asks():
    response = APIClient().post(
        "/api/v1/inquiries/fields/",
        {"service_type": "FLIGHT", "key": "from", "label_ar": "من", "label_en": "From"},
    )

    assert response.status_code in (401, 403)


def test_a_choice_field_needs_the_same_options_in_both_languages():
    """The website zips the two lists by position, so a missing line would put
    an Arabic label on an English answer."""
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = client.post(
        "/api/v1/inquiries/fields/",
        {
            "service_type": "FLIGHT",
            "key": "cabin",
            "label_ar": "الدرجة",
            "label_en": "Cabin",
            "field_type": "SELECT",
            "options_ar": "سياحية\nأعمال",
            "options_en": "Economy",
        },
    )

    assert response.status_code == 400


def test_options_are_served_zipped_for_the_form_to_render():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    client.post(
        "/api/v1/inquiries/fields/",
        {
            "service_type": "HOTEL",
            "key": "stars",
            "label_ar": "التصنيف",
            "label_en": "Rating",
            "field_type": "SELECT",
            "options_ar": "5 نجوم\n4 نجوم",
            "options_en": "5 stars\n4 stars",
        },
    )

    row = APIClient().get("/api/v1/inquiries/fields/").data["results"][0]

    assert row["options"] == [
        {"ar": "5 نجوم", "en": "5 stars"},
        {"ar": "4 نجوم", "en": "4 stars"},
    ]


def test_two_services_can_ask_the_same_question():
    """`key` is unique per service, not globally: a flight and a cruise both
    have a departure date and both file it under the same name."""
    InquiryField.objects.create(
        service_type="FLIGHT", key="depart", label_ar="المغادرة", label_en="Departure"
    )
    InquiryField.objects.create(
        service_type="CRUISE", key="depart", label_ar="الإبحار", label_en="Sailing"
    )

    assert InquiryField.objects.count() == 2

import pytest
from rest_framework.test import APIClient

from apps.inquiries.tests.factories import InquiryFactory
from apps.testimonials.tests.factories import TestimonialFactory
from apps.users.tests.factories import UserFactory
from common.constants import InquiryStatusChoices, RoleChoices

pytestmark = pytest.mark.django_db


def test_anonymous_users_are_rejected():
    client = APIClient()
    assert client.get("/api/v1/dashboard/stats/").status_code == 401


def test_staff_receives_the_documented_shape():
    InquiryFactory(status=InquiryStatusChoices.NEW)
    TestimonialFactory(is_approved=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.ADMIN))

    response = client.get("/api/v1/dashboard/stats/")

    assert response.status_code == 200
    assert set(response.data) == {"inquiries", "content", "testimonials"}
    assert set(response.data["inquiries"]) == {"total", "new", "by_status", "recent"}
    assert set(response.data["content"]) == {
        "destinations",
        "packages",
        "hotels",
        "flights",
        "visas",
        "offers",
        "testimonials",
    }
    assert response.data["inquiries"]["total"] == 1
    assert response.data["inquiries"]["new"] == 1
    assert response.data["testimonials"]["pending_approval"] == 1


def test_sales_staff_can_read_the_dashboard():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.SALES))
    assert client.get("/api/v1/dashboard/stats/").status_code == 200

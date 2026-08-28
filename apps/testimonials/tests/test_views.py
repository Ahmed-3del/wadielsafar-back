import pytest
from rest_framework.test import APIClient

from apps.testimonials.tests.factories import TestimonialFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices, ServiceTypeChoices

pytestmark = pytest.mark.django_db


def test_public_list_hides_unapproved_and_hidden_testimonials():
    TestimonialFactory(is_approved=True, is_visible=True)
    TestimonialFactory(is_approved=False, is_visible=True)
    TestimonialFactory(is_approved=True, is_visible=False)
    client = APIClient()
    response = client.get("/api/v1/testimonials/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_public_cannot_retrieve_an_unapproved_testimonial():
    testimonial = TestimonialFactory(is_approved=False)
    client = APIClient()
    assert client.get(f"/api/v1/testimonials/{testimonial.pk}/").status_code == 404


def test_staff_list_returns_everything():
    TestimonialFactory(is_approved=False)
    TestimonialFactory(is_approved=True, is_visible=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.ADMIN))
    assert client.get("/api/v1/testimonials/").data["count"] == 2


def test_staff_filters():
    TestimonialFactory(is_approved=False, rating=3, service_type=ServiceTypeChoices.HOTEL)
    TestimonialFactory(is_approved=True, rating=5, service_type=ServiceTypeChoices.FLIGHT)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.ADMIN))

    assert client.get("/api/v1/testimonials/", {"is_approved": "false"}).data["count"] == 1
    assert client.get("/api/v1/testimonials/", {"rating": 5}).data["count"] == 1
    assert client.get("/api/v1/testimonials/", {"service_type": "HOTEL"}).data["count"] == 1
    assert client.get("/api/v1/testimonials/", {"is_visible": "true"}).data["count"] == 2


def test_public_cannot_approve_a_testimonial():
    testimonial = TestimonialFactory(is_approved=False)
    client = APIClient()
    response = client.post(f"/api/v1/testimonials/{testimonial.pk}/approve/")
    assert response.status_code == 401
    testimonial.refresh_from_db()
    assert testimonial.is_approved is False


def test_sales_role_cannot_approve_a_testimonial():
    testimonial = TestimonialFactory(is_approved=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.SALES))
    response = client.post(f"/api/v1/testimonials/{testimonial.pk}/approve/")
    assert response.status_code == 403


def test_content_manager_can_approve_a_testimonial():
    testimonial = TestimonialFactory(is_approved=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    response = client.post(f"/api/v1/testimonials/{testimonial.pk}/approve/")
    assert response.status_code == 200
    assert response.data["is_approved"] is True
    testimonial.refresh_from_db()
    assert testimonial.is_approved is True


def test_public_cannot_create_a_testimonial():
    client = APIClient()
    response = client.post(
        "/api/v1/testimonials/",
        {"customer_name": "Sara", "content_ar": "جيد", "content_en": "Good", "rating": 5},
    )
    assert response.status_code == 401

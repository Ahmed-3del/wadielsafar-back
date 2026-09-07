import pytest
from rest_framework.test import APIClient

from apps.services.tests.factories import ServiceFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_public_list_only_returns_active_services():
    ServiceFactory(is_active=True)
    ServiceFactory(is_active=False)
    client = APIClient()
    response = client.get("/api/v1/services/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_staff_list_returns_inactive_services_too():
    ServiceFactory(is_active=True)
    ServiceFactory(is_active=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    response = client.get("/api/v1/services/")
    assert response.data["count"] == 2


def test_public_cannot_create_service():
    client = APIClient()
    response = client.post("/api/v1/services/", {"name_ar": "طيران", "name_en": "Flights"})
    assert response.status_code == 401


def test_content_manager_can_create_service():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    response = client.post(
        "/api/v1/services/",
        {"name_ar": "طيران", "name_en": "Flights", "icon": "plane", "order": 1},
    )
    assert response.status_code == 201
    assert response.data["slug"] == "flights"


def test_filter_by_is_active_for_staff():
    ServiceFactory(is_active=True)
    ServiceFactory(is_active=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.ADMIN))
    response = client.get("/api/v1/services/", {"is_active": "false"})
    assert response.data["count"] == 1


def as_editor():
    """The other tests in this file build this inline; the four below share it
    rather than repeating it a fourth time."""
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    return client


def test_icon_must_be_one_the_website_can_draw():
    """A free-text key was the old behaviour: whoever typed it had no way to
    know which words the site recognises, and an unknown one fell back to a
    generic mark without saying so."""
    response = as_editor().post(
        "/api/v1/services/",
        {"name_ar": "خدمة", "name_en": "Service", "icon": "unicorn"},
    )

    assert response.status_code == 400
    assert "icon" in response.data["error"]["details"]


def test_a_service_link_must_be_a_path_on_this_site():
    """The website renders it through a localised Link, so an absolute URL
    would come out as /ar/https://example.com."""
    response = as_editor().post(
        "/api/v1/services/",
        {
            "name_ar": "خدمة",
            "name_en": "External service",
            "link": "https://example.com",
        },
    )

    assert response.status_code == 400


def test_a_service_can_point_at_a_page_on_this_site():
    response = as_editor().post(
        "/api/v1/services/",
        {"name_ar": "تأشيرة", "name_en": "Visa tile", "icon": "passport", "link": "/visas"},
    )

    assert response.status_code == 201, response.data
    assert response.data["link"] == "/visas"


def test_a_blank_link_is_allowed_and_means_the_contact_form():
    response = as_editor().post(
        "/api/v1/services/",
        {"name_ar": "خدمة", "name_en": "Default service", "icon": "car"},
    )

    assert response.status_code == 201, response.data
    assert response.data["link"] == ""


def test_a_tile_can_say_which_service_the_form_should_land_on():
    """So a reader who pressed "Travel insurance" is not asked again what they
    came for."""
    response = as_editor().post(
        "/api/v1/services/",
        {
            "name_ar": "تأمين السفر",
            "name_en": "Travel Insurance",
            "icon": "shield",
            "service_type": "OTHER",
        },
    )

    assert response.status_code == 201, response.data
    assert response.data["service_type"] == "OTHER"


def test_a_tile_cannot_point_at_a_service_no_enquiry_can_be_filed_under():
    response = as_editor().post(
        "/api/v1/services/",
        {"name_ar": "خدمة", "name_en": "Service", "service_type": "SAFARI"},
    )

    assert response.status_code == 400


def test_a_tile_need_not_name_a_service():
    response = as_editor().post(
        "/api/v1/services/", {"name_ar": "خدمة", "name_en": "Unmapped service"}
    )

    assert response.status_code == 201, response.data
    assert response.data["service_type"] == ""

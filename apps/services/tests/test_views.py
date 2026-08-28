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

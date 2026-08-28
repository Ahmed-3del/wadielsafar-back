import pytest
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_user_list_requires_authentication():
    client = APIClient()
    response = client.get("/api/v1/users/")
    assert response.status_code == 401


def test_user_list_accessible_to_staff_role():
    staff = UserFactory(role=RoleChoices.ADMIN)
    client = APIClient()
    client.force_authenticate(user=staff)
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert "results" in response.data

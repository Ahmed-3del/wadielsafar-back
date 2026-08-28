import pytest
from rest_framework.test import APIClient

from apps.pages.tests.factories import PageFactory

pytestmark = pytest.mark.django_db


def test_public_list_returns_200():
    PageFactory()
    client = APIClient()
    response = client.get("/api/v1/pages/")
    assert response.status_code == 200
    assert response.data["count"] == 1

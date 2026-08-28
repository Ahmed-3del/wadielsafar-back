import pytest
from rest_framework.test import APIClient

from apps.packages.tests.factories import PackageFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_public_list_only_returns_active_packages():
    PackageFactory(is_active=True)
    PackageFactory(is_active=False)
    client = APIClient()
    response = client.get("/api/v1/packages/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_filter_by_price_range():
    PackageFactory(price_from="1000.00")
    PackageFactory(price_from="5000.00")
    client = APIClient()
    response = client.get("/api/v1/packages/", {"price_min": "2000"})
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_featured_action_returns_only_featured():
    PackageFactory(is_featured=True)
    PackageFactory(is_featured=False)
    client = APIClient()
    response = client.get("/api/v1/packages/featured/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_admin_can_create_package():
    admin = UserFactory(role=RoleChoices.ADMIN)
    category = PackageFactory().category
    destination = PackageFactory().destination
    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.post(
        "/api/v1/packages/",
        {
            "title_ar": "رحلة",
            "title_en": "Trip",
            "category_id": category.id,
            "destination_id": destination.id,
            "price_from": "999.99",
            "duration_days": 5,
        },
    )
    assert response.status_code == 201
    assert response.data["slug"] == "trip"

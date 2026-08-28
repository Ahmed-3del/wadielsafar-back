import pytest
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory
from apps.visas.tests.factories import VisaCountryFactory, VisaTypeFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_public_list_only_returns_active_countries():
    VisaCountryFactory(is_active=True)
    VisaCountryFactory(is_active=False)
    client = APIClient()
    response = client.get("/api/v1/visas/countries/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_public_create_visa_type_is_forbidden():
    client = APIClient()
    response = client.post("/api/v1/visas/", {"name_en": "x"})
    assert response.status_code in (401, 403)


def test_admin_can_create_visa_type():
    admin = UserFactory(role=RoleChoices.SUPER_ADMIN)
    country = VisaCountryFactory()
    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.post(
        "/api/v1/visas/",
        {
            "country_id": country.id,
            "name_ar": "سياحية",
            "name_en": "Tourist",
            "price": "250.00",
            "processing_time_days": 3,
        },
    )
    assert response.status_code == 201


def test_purpose_filters_visa_types():
    """The homepage asks what the visa is for before anything else."""
    country = VisaCountryFactory(is_active=True)
    VisaTypeFactory(country=country, name_en="Tourist", purpose="TOURISM", is_active=True)
    VisaTypeFactory(country=country, name_en="Business", purpose="BUSINESS", is_active=True)

    response = APIClient().get("/api/v1/visas/", {"purpose": "BUSINESS"})

    assert response.status_code == 200
    assert [row["name_en"] for row in response.data["results"]] == ["Business"]


def test_visa_type_without_a_purpose_is_not_filed_under_one():
    """Blank means unlabelled, so it must not answer to a specific purpose."""
    country = VisaCountryFactory(is_active=True)
    VisaTypeFactory(country=country, name_en="Unlabelled", purpose="", is_active=True)

    filtered = APIClient().get("/api/v1/visas/", {"purpose": "TOURISM"})
    unfiltered = APIClient().get("/api/v1/visas/")

    assert filtered.data["count"] == 0
    assert unfiltered.data["count"] == 1

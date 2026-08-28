import pytest
from rest_framework.test import APIClient

from apps.destinations.tests.factories import DestinationFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_public_list_only_returns_active_destinations():
    DestinationFactory(is_active=True)
    DestinationFactory(is_active=False)
    client = APIClient()
    response = client.get("/api/v1/destinations/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_public_create_is_forbidden():
    client = APIClient()
    response = client.post(
        "/api/v1/destinations/", {"name_ar": "test", "name_en": "test", "country_ar": "test", "country_en": "KSA"}
    )
    assert response.status_code in (401, 403)


def test_editor_can_create_destination():
    editor = UserFactory(role=RoleChoices.EDITOR)
    client = APIClient()
    client.force_authenticate(user=editor)
    response = client.post(
        "/api/v1/destinations/",
        {
            "name_ar": "الرياض",
            "name_en": "Riyadh",
            "country_ar": "السعودية",
            "country_en": "Saudi Arabia",
        },
    )
    assert response.status_code == 201
    assert response.data["slug"] == "riyadh"


def test_country_filter_matches_either_language():
    """One `country` parameter, two columns: an Arabic client filters in Arabic."""
    DestinationFactory(name_en="Dubai", country_ar="الإمارات", country_en="United Arab Emirates")
    DestinationFactory(name_en="Riyadh", country_ar="السعودية", country_en="Saudi Arabia")
    client = APIClient()

    arabic = client.get("/api/v1/destinations/", {"country": "الإمارات"})
    assert [row["name_en"] for row in arabic.data["results"]] == ["Dubai"]

    english = client.get("/api/v1/destinations/", {"country": "saudi arabia"})
    assert [row["name_en"] for row in english.data["results"]] == ["Riyadh"]

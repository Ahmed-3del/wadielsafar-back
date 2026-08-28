import pytest
from rest_framework.test import APIClient

from apps.partners.models import Partner
from apps.partners.tests.factories import PartnerFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_public_list_hides_inactive_partners():
    PartnerFactory(is_active=True)
    PartnerFactory(is_active=False)

    response = APIClient().get("/api/v1/partners/")

    assert response.status_code == 200
    assert response.data["count"] == 1


def test_content_manager_still_sees_what_they_switched_off():
    PartnerFactory(is_active=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    assert client.get("/api/v1/partners/").data["count"] == 1


def test_public_cannot_create_a_partner():
    response = APIClient().post(
        "/api/v1/partners/", {"name_ar": "شريك", "name_en": "Partner"}
    )

    assert response.status_code in (401, 403)
    assert Partner.objects.count() == 0


def test_editor_can_create_a_partner():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = client.post(
        "/api/v1/partners/",
        {"name_ar": "طيران ناس", "name_en": "flynas", "logo": "https://cdn.example.com/f.png"},
    )

    assert response.status_code == 201, response.data
    assert Partner.objects.get().name_en == "flynas"


def test_partners_come_back_in_the_order_editors_set():
    PartnerFactory(name_en="Third", order=3)
    PartnerFactory(name_en="First", order=1)
    PartnerFactory(name_en="Second", order=2)

    response = APIClient().get("/api/v1/partners/")

    assert [row["name_en"] for row in response.data["results"]] == ["First", "Second", "Third"]


def test_website_is_optional():
    """Plenty of partners have no site worth linking to."""
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = client.post("/api/v1/partners/", {"name_ar": "شريك", "name_en": "Partner"})

    assert response.status_code == 201, response.data
    assert response.data["website_url"] == ""

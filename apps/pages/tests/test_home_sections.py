import pytest
from rest_framework.test import APIClient

from apps.pages.models import HomeSection
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db

LIST_URL = "/api/v1/pages/home-sections/"
REORDER_URL = f"{LIST_URL}reorder/"


def as_editor():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    return client


def keys(response):
    rows = response.data["results"] if "results" in response.data else response.data
    return [row["key"] for row in rows]


def test_the_shipped_running_order_is_there():
    """The homepage is assembled from this list, so an empty table renders a
    page with nothing under the hero."""
    response = APIClient().get(LIST_URL, {"page_size": 20})

    assert response.status_code == 200
    assert keys(response)[0] == "SERVICES"


def test_public_sees_only_the_sections_that_are_switched_on():
    HomeSection.objects.update(is_active=True)
    HomeSection.objects.filter(key="CRUISES").update(is_active=False)

    assert "CRUISES" not in keys(APIClient().get(LIST_URL, {"page_size": 20}))


def test_editor_still_sees_a_section_they_switched_off():
    """Otherwise there is no way back — it would vanish from the panel too."""
    HomeSection.objects.filter(key="CRUISES").update(is_active=False)

    assert "CRUISES" in keys(as_editor().get(LIST_URL, {"page_size": 20}))


def test_public_cannot_reorder_the_homepage():
    response = APIClient().post(REORDER_URL, {"keys": ["CTA", "SERVICES"]}, format="json")

    assert response.status_code in (401, 403)


def test_editor_can_reorder_the_homepage():
    order = ["CTA", "TRUST", "SERVICES"]
    response = as_editor().post(REORDER_URL, {"keys": order}, format="json")

    assert response.status_code == 200, response.data
    positions = {s.key: s.order for s in HomeSection.objects.all()}
    assert positions["CTA"] < positions["TRUST"] < positions["SERVICES"]


def test_reorder_rejects_a_section_that_does_not_exist():
    """A typo would otherwise silently leave the order untouched."""
    response = as_editor().post(REORDER_URL, {"keys": ["SERVICES", "NOPE"]}, format="json")

    assert response.status_code == 400
    assert "NOPE" in str(response.data)


def test_reorder_rejects_a_section_listed_twice():
    response = as_editor().post(REORDER_URL, {"keys": ["SERVICES", "SERVICES"]}, format="json")

    assert response.status_code == 400


def test_sections_cannot_be_created():
    """A row with no component behind it renders nothing at all."""
    response = as_editor().post(LIST_URL, {"key": "SERVICES", "order": 0}, format="json")

    assert response.status_code == 405


def test_sections_cannot_be_deleted():
    """Deleting one would make it unreachable from the panel for good."""
    section = HomeSection.objects.first()

    assert as_editor().delete(f"{LIST_URL}{section.pk}/").status_code == 405


def test_editor_can_switch_a_section_off():
    section = HomeSection.objects.get(key="TESTIMONIALS")

    response = as_editor().patch(f"{LIST_URL}{section.pk}/", {"is_active": False}, format="json")

    assert response.status_code == 200, response.data
    section.refresh_from_db()
    assert section.is_active is False


def test_every_section_carries_a_readable_label():
    """The panel lists these; a bare key like TESTIMONIALS is not a UI."""
    response = as_editor().get(LIST_URL, {"page_size": 20})

    rows = response.data["results"] if "results" in response.data else response.data
    for row in rows:
        assert row["label"] and row["label"] != row["key"]

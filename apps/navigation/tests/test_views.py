import pytest
from rest_framework.test import APIClient

from apps.navigation.models import NavItem
from apps.navigation.tests.factories import NavItemFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


@pytest.fixture
def clean_nav():
    """The default navigation ships in a data migration, so it is already in
    the test database. Tests that count rows need to start from empty."""
    NavItem.objects.all().delete()


def test_public_list_hides_switched_off_links(clean_nav):
    NavItemFactory(is_active=True)
    NavItemFactory(is_active=False)

    response = APIClient().get("/api/v1/navigation/")

    assert response.status_code == 200
    # Unpaginated on purpose: the header wants the whole set in one request.
    assert len(response.data) == 1


def test_content_manager_sees_the_links_they_switched_off(clean_nav):
    NavItemFactory(is_active=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    assert len(client.get("/api/v1/navigation/").data) == 1


def test_links_come_back_grouped_then_ordered(clean_nav):
    NavItemFactory(label_en="Second", group="PRIMARY", order=2)
    NavItemFactory(label_en="Footer", group="SECONDARY", order=1)
    NavItemFactory(label_en="First", group="PRIMARY", order=1)

    response = APIClient().get("/api/v1/navigation/")

    assert [row["label_en"] for row in response.data] == ["First", "Second", "Footer"]


def test_public_cannot_add_a_link(clean_nav):
    response = APIClient().post(
        "/api/v1/navigation/", {"label_ar": "x", "label_en": "x", "href": "/x"}
    )

    assert response.status_code in (401, 403)
    assert NavItem.objects.count() == 0


@pytest.mark.parametrize("href", ["https://evil.example.com", "//evil.example.com", "packages"])
def test_href_must_be_a_path_on_this_site(href):
    """An arbitrary host in the header is an open redirect wearing a nav label."""
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = client.post(
        "/api/v1/navigation/", {"label_ar": "س", "label_en": "x", "href": href}
    )

    assert response.status_code == 400
    assert "href" in response.data["error"]["details"]


def test_editor_can_add_a_link(clean_nav):
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = client.post(
        "/api/v1/navigation/",
        {"label_ar": "المدونة", "label_en": "Blog", "href": "/blog", "group": "PRIMARY"},
    )

    assert response.status_code == 201, response.data
    assert NavItem.objects.get().href == "/blog"


def test_default_navigation_is_seeded():
    """A fresh install must not come up with an empty header."""
    assert NavItem.objects.filter(group="PRIMARY").count() >= 1

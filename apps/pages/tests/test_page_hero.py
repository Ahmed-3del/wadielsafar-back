import pytest
from rest_framework.test import APIClient

from apps.pages.models import HeroMediaChoices, PageHero
from apps.pages.serializers import PageHeroSerializer
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def _hero(**overrides):
    defaults = {
        "page_key": "home",
        "media_type": HeroMediaChoices.IMAGE,
        "image_url": "https://cdn.example.com/hero.jpg",
    }
    return PageHero.objects.create(**{**defaults, **overrides})


def test_public_can_read_active_hero_by_page_key():
    _hero()
    response = APIClient().get("/api/v1/pages/heroes/home/")
    assert response.status_code == 200
    assert response.data["media_type"] == "IMAGE"


def test_public_cannot_see_inactive_hero():
    _hero(is_active=False)
    assert APIClient().get("/api/v1/pages/heroes/home/").status_code == 404


def test_public_cannot_write():
    response = APIClient().post("/api/v1/pages/heroes/", {"page_key": "about"})
    assert response.status_code in (401, 403)


def test_staff_can_create_hero():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    response = client.post(
        "/api/v1/pages/heroes/",
        {
            "page_key": "visas",
            "media_type": "VIDEO",
            "video_url": "https://cdn.example.com/hero.mp4",
            "poster_url": "https://cdn.example.com/poster.jpg",
        },
    )
    assert response.status_code == 201, response.data


@pytest.mark.parametrize(
    ("media_type", "missing_field"),
    [("IMAGE", "image_url"), ("VIDEO", "video_url")],
)
def test_media_type_requires_its_source(media_type, missing_field):
    serializer = PageHeroSerializer(data={"page_key": "about", "media_type": media_type})
    assert not serializer.is_valid()
    assert missing_field in serializer.errors


def test_gradient_hero_needs_no_media():
    serializer = PageHeroSerializer(data={"page_key": "about", "media_type": "NONE"})
    assert serializer.is_valid(), serializer.errors


def test_page_key_is_unique():
    _hero()
    serializer = PageHeroSerializer(data={"page_key": "home", "media_type": "NONE"})
    assert not serializer.is_valid()
    assert "page_key" in serializer.errors

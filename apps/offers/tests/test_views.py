import datetime

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.offers.tests.factories import OfferFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices, ServiceTypeChoices

pytestmark = pytest.mark.django_db

TODAY = timezone.localdate()


def _days(count):
    return datetime.timedelta(days=count)


def test_public_list_only_returns_active_offers():
    OfferFactory(is_active=True)
    OfferFactory(is_active=False)
    client = APIClient()
    response = client.get("/api/v1/offers/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_retrieve_by_slug_exposes_computed_fields():
    offer = OfferFactory(title_en="Winter Escape")
    client = APIClient()
    response = client.get(f"/api/v1/offers/{offer.slug}/")
    assert response.status_code == 200
    assert response.data["status"] == "ACTIVE"
    assert response.data["discount_percentage"] == 25


def test_active_action_returns_unpaginated_offers_covering_today():
    OfferFactory(starts_at=TODAY, ends_at=TODAY + _days(2))
    OfferFactory(starts_at=TODAY + _days(3), ends_at=TODAY + _days(9))
    client = APIClient()
    response = client.get("/api/v1/offers/active/", {"limit": 6})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["status"] == "ACTIVE"


def test_status_filter_maps_to_date_comparisons():
    OfferFactory(starts_at=TODAY - _days(1), ends_at=TODAY + _days(1))
    OfferFactory(starts_at=TODAY + _days(2), ends_at=TODAY + _days(5))
    OfferFactory(starts_at=TODAY - _days(9), ends_at=TODAY - _days(2))
    client = APIClient()

    assert client.get("/api/v1/offers/", {"status": "ACTIVE"}).data["count"] == 1
    assert client.get("/api/v1/offers/", {"status": "SCHEDULED"}).data["count"] == 1
    assert client.get("/api/v1/offers/", {"status": "EXPIRED"}).data["count"] == 1


def test_filter_by_service_type_and_featured():
    OfferFactory(service_type=ServiceTypeChoices.FLIGHT, is_featured=True)
    OfferFactory(service_type=ServiceTypeChoices.HOTEL, is_featured=False)
    client = APIClient()

    assert client.get("/api/v1/offers/", {"service_type": "FLIGHT"}).data["count"] == 1
    assert client.get("/api/v1/offers/", {"is_featured": "true"}).data["count"] == 1


def test_public_cannot_create_an_offer():
    client = APIClient()
    response = client.post("/api/v1/offers/", {"title_en": "Nope"})
    assert response.status_code == 401


def test_content_manager_can_create_an_offer():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    response = client.post(
        "/api/v1/offers/",
        {
            "title_ar": "عرض الصيف",
            "title_en": "Summer Sale",
            "service_type": "PACKAGE",
            "price_before": "1000.00",
            "price_after": "800.00",
            "starts_at": str(TODAY),
            "ends_at": str(TODAY + _days(10)),
        },
    )
    assert response.status_code == 201
    assert response.data["slug"] == "summer-sale"
    assert response.data["discount_percentage"] == 20
    assert response.data["status"] == "ACTIVE"

import pytest

from apps.services.tests.factories import ServiceFactory

pytestmark = pytest.mark.django_db


def test_service_str_returns_english_name():
    service = ServiceFactory(name_en="Flight Booking")
    assert str(service) == "Flight Booking"


def test_slug_is_generated_from_english_name():
    service = ServiceFactory(name_en="Flight Booking")
    assert service.slug == "flight-booking"


def test_slug_is_disambiguated_for_duplicate_names():
    first = ServiceFactory(name_en="Flight Booking")
    second = ServiceFactory(name_en="Flight Booking")
    assert first.slug != second.slug


def test_default_ordering_is_by_order_then_english_name():
    from apps.services.models import Service

    ServiceFactory(name_en="B service", order=2)
    ServiceFactory(name_en="A service", order=1)
    assert [s.order for s in Service.objects.all()] == [1, 2]

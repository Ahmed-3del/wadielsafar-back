import pytest

from apps.dashboard.services import DashboardService
from apps.destinations.tests.factories import DestinationFactory
from apps.flights.tests.factories import FlightDealFactory
from apps.hotels.tests.factories import HotelFactory
from apps.inquiries.tests.factories import InquiryFactory
from apps.offers.tests.factories import OfferFactory
from apps.packages.tests.factories import PackageFactory
from apps.testimonials.tests.factories import TestimonialFactory
from apps.visas.tests.factories import VisaTypeFactory
from common.constants import InquiryStatusChoices

pytestmark = pytest.mark.django_db


def test_inquiry_totals_and_status_breakdown():
    InquiryFactory.create_batch(3, status=InquiryStatusChoices.NEW)
    InquiryFactory(status=InquiryStatusChoices.CONTACTED)
    InquiryFactory(status=InquiryStatusChoices.CONVERTED)

    stats = DashboardService.get_stats()["inquiries"]

    assert stats["total"] == 5
    assert stats["new"] == 3
    assert stats["by_status"] == {
        "NEW": 3,
        "CONTACTED": 1,
        "QUALIFIED": 0,
        "CONVERTED": 1,
        "CLOSED": 0,
    }


def test_by_status_lists_every_status_even_when_zero():
    stats = DashboardService.get_stats()["inquiries"]
    assert set(stats["by_status"]) == {choice.value for choice in InquiryStatusChoices}
    assert set(stats["by_status"].values()) == {0}


def test_recent_returns_the_five_newest_inquiries():
    inquiries = [InquiryFactory() for _ in range(7)]

    recent = DashboardService.get_stats()["inquiries"]["recent"]

    assert len(recent) == 5
    assert [row["id"] for row in recent] == [i.pk for i in reversed(inquiries[-5:])]
    assert set(recent[0]) == {"id", "name", "service_type", "status", "created_at"}


def test_content_counts_only_include_active_records():
    DestinationFactory(is_active=True)
    DestinationFactory(is_active=False)
    PackageFactory(is_active=True)
    HotelFactory(is_active=True)
    HotelFactory(is_active=False)
    FlightDealFactory(is_active=True)
    VisaTypeFactory(is_active=True)
    OfferFactory(is_active=True)
    TestimonialFactory(is_approved=True, is_visible=True)
    TestimonialFactory(is_approved=False)

    content = DashboardService.get_stats()["content"]

    # PackageFactory and HotelFactory each create their own destination.
    assert content["destinations"] >= 1
    assert content["packages"] == 1
    assert content["hotels"] == 1
    assert content["flights"] == 1
    assert content["visas"] == 1
    assert content["offers"] == 1
    assert content["testimonials"] == 1


def test_pending_approval_counts_unapproved_testimonials():
    TestimonialFactory(is_approved=True)
    TestimonialFactory.create_batch(2, is_approved=False)

    assert DashboardService.get_stats()["testimonials"]["pending_approval"] == 2


def test_stats_are_built_from_a_small_fixed_number_of_queries(django_assert_max_num_queries):
    InquiryFactory.create_batch(6)
    TestimonialFactory.create_batch(4)

    with django_assert_max_num_queries(10):
        DashboardService.get_stats()

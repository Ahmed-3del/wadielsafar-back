import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.destinations.tests.factories import DestinationFactory
from apps.packages.models import Package, PackageItinerary

pytestmark = pytest.mark.django_db


@pytest.fixture
def demo_destinations():
    """The slugs the seed content refers to. Anything missing is skipped, not fatal."""
    for slug in ("dubai", "istanbul", "georgia", "maldives"):
        DestinationFactory(slug=slug, name_en=slug.title())


def test_seed_fills_the_sections_the_detail_page_renders(demo_destinations):
    call_command("seed_demo_packages", force=True)

    package = Package.objects.get(slug="dubai-family-package")
    assert package.description_ar and package.description_en
    assert package.included_services_ar and package.included_services_en
    # The page draws a day per line, so the count has to match what is sold.
    assert package.itinerary.count() == package.duration_days


def test_seed_is_idempotent(demo_destinations):
    call_command("seed_demo_packages", force=True)
    call_command("seed_demo_packages", force=True)

    package = Package.objects.get(slug="dubai-family-package")
    assert package.itinerary.count() == 5
    assert Package.objects.filter(slug="dubai-family-package").count() == 1


def test_seed_drops_days_left_over_from_a_longer_programme(demo_destinations):
    call_command("seed_demo_packages", force=True)
    package = Package.objects.get(slug="dubai-family-package")
    PackageItinerary.objects.create(
        package=package, day_number=99, title_ar="زائد", title_en="Stale"
    )

    call_command("seed_demo_packages", force=True)

    assert not package.itinerary.filter(day_number=99).exists()


def test_seed_skips_packages_whose_destination_is_missing():
    """No destinations at all: the command reports and moves on rather than crashing."""
    call_command("seed_demo_packages", force=True)

    assert Package.objects.count() == 0


def test_seed_refuses_to_run_outside_debug_without_force(settings):
    settings.DEBUG = False

    with pytest.raises(CommandError, match="DEBUG is off"):
        call_command("seed_demo_packages")

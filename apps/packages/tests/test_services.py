import pytest

from apps.packages.services import PackageService
from apps.packages.tests.factories import PackageFactory, PackageItineraryFactory

pytestmark = pytest.mark.django_db


def test_get_featured_only_returns_active_featured_packages():
    PackageFactory(is_featured=True, is_active=True)
    PackageFactory(is_featured=False, is_active=True)
    PackageFactory(is_featured=True, is_active=False)

    featured = list(PackageService.get_featured(limit=10))

    assert len(featured) == 1


def test_compute_duration_days_derives_from_itinerary_count():
    package = PackageFactory(duration_days=1)
    PackageItineraryFactory(package=package, day_number=1)
    PackageItineraryFactory(package=package, day_number=2)
    PackageItineraryFactory(package=package, day_number=3)

    duration = PackageService.compute_duration_days(package)

    assert duration == 3
    package.refresh_from_db()
    assert package.duration_days == 3

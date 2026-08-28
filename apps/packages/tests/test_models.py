import pytest
from django.db import IntegrityError

from apps.packages.tests.factories import PackageFactory, PackageItineraryFactory

pytestmark = pytest.mark.django_db


def test_package_slug_auto_generated_from_title_en():
    package = PackageFactory(title_en="Red Sea Escape", slug="")
    assert package.slug == "red-sea-escape"


def test_itinerary_day_number_unique_per_package():
    package = PackageFactory()
    PackageItineraryFactory(package=package, day_number=1)
    with pytest.raises(IntegrityError):
        PackageItineraryFactory(package=package, day_number=1)

import pytest

from apps.packages.serializers import PackageDetailSerializer
from apps.packages.tests.factories import PackageFactory, PackageItineraryFactory

pytestmark = pytest.mark.django_db


def test_package_detail_serializer_nests_itinerary_and_destination():
    package = PackageFactory()
    PackageItineraryFactory(package=package, day_number=1)
    PackageItineraryFactory(package=package, day_number=2)

    data = PackageDetailSerializer(package).data

    assert len(data["itinerary"]) == 2
    assert data["destination"]["id"] == package.destination.id
    assert data["category"]["name_en"] == package.category.name_en

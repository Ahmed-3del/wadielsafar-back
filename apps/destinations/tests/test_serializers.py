import pytest

from apps.destinations.serializers import DestinationSerializer
from apps.destinations.tests.factories import DestinationFactory

pytestmark = pytest.mark.django_db


def test_destination_serializer_includes_bilingual_fields():
    destination = DestinationFactory(name_ar="جدة", name_en="Jeddah")
    data = DestinationSerializer(destination).data
    assert data["name_ar"] == "جدة"
    assert data["name_en"] == "Jeddah"
    assert data["slug"] == destination.slug

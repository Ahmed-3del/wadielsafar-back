import pytest

from apps.visas.serializers import VisaTypeSerializer
from apps.visas.tests.factories import VisaTypeFactory

pytestmark = pytest.mark.django_db


def test_visa_type_serializer_nests_country():
    visa_type = VisaTypeFactory()
    data = VisaTypeSerializer(visa_type).data
    assert data["country"]["id"] == visa_type.country.id

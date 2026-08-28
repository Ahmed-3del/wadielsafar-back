import pytest

from apps.visas.tests.factories import VisaTypeFactory

pytestmark = pytest.mark.django_db


def test_visa_type_str_includes_country_and_name():
    visa_type = VisaTypeFactory(name_en="Tourist", country__name_en="Egypt")
    assert str(visa_type) == "Egypt - Tourist"

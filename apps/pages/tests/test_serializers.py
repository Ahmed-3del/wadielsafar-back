import pytest

from apps.pages.serializers import PageSerializer
from apps.pages.tests.factories import PageFactory

pytestmark = pytest.mark.django_db


def test_page_serializer_includes_name():
    obj = PageFactory(name="Sample Page")
    data = PageSerializer(obj).data
    assert data["name"] == "Sample Page"

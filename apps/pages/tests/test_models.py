import pytest

from apps.pages.tests.factories import PageFactory

pytestmark = pytest.mark.django_db


def test_page_str_returns_name():
    obj = PageFactory(name="Sample Page")
    assert str(obj) == "Sample Page"

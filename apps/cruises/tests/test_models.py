import pytest

from apps.cruises.tests.factories import CruiseFactory

pytestmark = pytest.mark.django_db


def test_slug_is_generated_from_english_title():
    cruise = CruiseFactory(title_en="Red Sea Escape")
    assert cruise.slug == "red-sea-escape"


def test_slugs_stay_unique_for_duplicate_titles():
    first = CruiseFactory(title_en="Med Voyage")
    second = CruiseFactory(title_en="Med Voyage")
    assert first.slug != second.slug

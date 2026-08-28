import pytest

from apps.destinations.tests.factories import DestinationFactory

pytestmark = pytest.mark.django_db


def test_slug_auto_generated_from_name_en():
    destination = DestinationFactory(name_en="Jeddah Coast", slug="")
    assert destination.slug == "jeddah-coast"


def test_duplicate_name_en_generates_unique_slug():
    DestinationFactory(name_en="AlUla", slug="")
    second = DestinationFactory(name_en="AlUla", slug="")
    assert second.slug == "alula-2"

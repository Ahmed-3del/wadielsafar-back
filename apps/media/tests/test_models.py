import pytest

from apps.media.tests.factories import MediaFactory

pytestmark = pytest.mark.django_db


def test_media_str_returns_file_name():
    media = MediaFactory()
    assert str(media) == media.file.name

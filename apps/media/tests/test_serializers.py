import pytest

from apps.media.serializers import MediaSerializer
from apps.media.tests.factories import MediaFactory

pytestmark = pytest.mark.django_db


def test_media_serializer_exposes_bilingual_alt_text():
    media = MediaFactory(alt_text_ar="بديل", alt_text_en="alt")
    data = MediaSerializer(media).data
    assert data["alt_text_ar"] == "بديل"
    assert data["alt_text_en"] == "alt"

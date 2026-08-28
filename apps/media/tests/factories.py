import factory
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.media.models import Media


class MediaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Media

    file = factory.LazyFunction(
        lambda: SimpleUploadedFile("shot.jpg", b"content", content_type="image/jpeg")
    )
    alt_text_en = "Test asset"

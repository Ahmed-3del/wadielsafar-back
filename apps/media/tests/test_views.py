import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.media.models import Media
from apps.media.tests.factories import MediaFactory
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_upload_requires_authentication():
    client = APIClient()
    file = SimpleUploadedFile("shot.jpg", b"content", content_type="image/jpeg")
    response = client.post("/api/v1/media/", {"file": file}, format="multipart")
    assert response.status_code == 401


def test_authenticated_staff_can_upload_and_it_records_uploader(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)
    file = SimpleUploadedFile("shot.jpg", b"content", content_type="image/jpeg")
    response = client.post("/api/v1/media/", {"file": file}, format="multipart")
    assert response.status_code == 201
    assert response.data["uploaded_by"] == user.id


def test_staff_can_delete_media(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    upload = SimpleUploadedFile("shot.jpg", b"binary-content", content_type="image/jpeg")
    created = client.post("/api/v1/media/", {"file": upload}, format="multipart")
    assert created.status_code == 201, created.data

    response = client.delete(f"/api/v1/media/{created.data['id']}/")
    assert response.status_code == 204
    assert Media.objects.count() == 0


def test_public_cannot_delete_media(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    media = MediaFactory()
    response = APIClient().delete(f"/api/v1/media/{media.id}/")
    assert response.status_code in (401, 403)
    assert Media.objects.count() == 1


def _upload(client, name, content=b"x", content_type="image/jpeg"):
    return client.post(
        "/api/v1/media/",
        {"file": SimpleUploadedFile(name, content, content_type=content_type)},
        format="multipart",
    )


def test_upload_accepts_images_and_video(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    image = _upload(client, "hero.jpg")
    assert image.status_code == 201, image.data
    assert image.data["kind"] == "IMAGE"

    video = _upload(client, "hero.mp4", content_type="video/mp4")
    assert video.status_code == 201, video.data
    assert video.data["kind"] == "VIDEO"


def test_upload_accepts_a_pdf_certificate(tmp_path, settings):
    """The company publishes its licences from the library, so PDFs have to
    land here — SVG still must not."""
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = _upload(client, "licence.pdf", content_type="application/pdf")

    assert response.status_code == 201, response.data
    assert response.data["kind"] == "DOCUMENT"


def test_upload_rejects_a_pdf_over_its_own_size_limit(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    response = _upload(
        client, "huge.pdf", content=b"x" * (16 * 1024 * 1024 + 1), content_type="application/pdf"
    )

    assert response.status_code == 400
    assert Media.objects.count() == 0


def test_upload_rejects_unsupported_types(tmp_path, settings):
    """Including SVG, which a browser treats as a document that can carry script."""
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    for name in ("notes.txt", "payload.svg", "run.html"):
        response = _upload(client, name)
        assert response.status_code == 400, f"{name} was accepted"
        assert "file" in response.data["error"]["details"]


def test_upload_rejects_files_over_the_size_limit(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))

    oversized = _upload(client, "huge.jpg", content=b"x" * (8 * 1024 * 1024 + 1))
    assert oversized.status_code == 400
    assert Media.objects.count() == 0

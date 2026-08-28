from pathlib import Path

from rest_framework import serializers

from apps.media.models import Media

# Uploads are served from the same origin as the panel and the API, so the
# extension list is the control that matters: Django serves each file with the
# content type its extension implies. SVG is deliberately absent — it is an
# image everywhere except in a browser, where it is a document that can carry
# script.
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"})
VIDEO_EXTENSIONS = frozenset({".mp4", ".webm", ".mov", ".m4v"})
# PDF only. The company's certificates are published from here, and unlike SVG
# a PDF's own scripting runs inside the viewer's sandbox rather than in the
# page's origin. Uploading still requires a staff account.
DOCUMENT_EXTENSIONS = frozenset({".pdf"})

# Generous enough for a hero photograph and a short background clip, small
# enough that a mistaken upload cannot fill the disk. A production deployment
# has to raise the proxy's own body limit to match the video figure.
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_VIDEO_BYTES = 64 * 1024 * 1024
# A scanned government certificate runs to a couple of megabytes.
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024


def classify(name: str) -> str | None:
    suffix = Path(name).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "IMAGE"
    if suffix in VIDEO_EXTENSIONS:
        return "VIDEO"
    if suffix in DOCUMENT_EXTENSIONS:
        return "DOCUMENT"
    return None


class MediaSerializer(serializers.ModelSerializer):
    # Lets the panel preview a still differently from a clip, and filter the
    # picker to whichever the field being filled in actually accepts.
    kind = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = (
            "id",
            "file",
            "kind",
            "alt_text_ar",
            "alt_text_en",
            "uploaded_by",
            "created_at",
        )
        read_only_fields = ("id", "kind", "uploaded_by", "created_at")

    def get_kind(self, obj: Media) -> str:
        return classify(obj.file.name) or "OTHER"

    def validate_file(self, value):
        kind = classify(value.name)
        if kind is None:
            allowed = ", ".join(sorted(IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | DOCUMENT_EXTENSIONS))
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed extensions: {allowed}."
            )

        limit = {
            "IMAGE": MAX_IMAGE_BYTES,
            "VIDEO": MAX_VIDEO_BYTES,
            "DOCUMENT": MAX_DOCUMENT_BYTES,
        }[kind]
        if value.size > limit:
            raise serializers.ValidationError(
                f"File is too large. {kind.title()} uploads are limited to "
                f"{limit // (1024 * 1024)} MB."
            )
        return value

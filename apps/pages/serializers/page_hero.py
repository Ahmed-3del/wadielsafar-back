from rest_framework import serializers

from apps.pages.models import HeroMediaChoices, PageHero


class PageHeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageHero
        fields = (
            "id",
            "page_key",
            "media_type",
            "image_url",
            "video_url",
            "poster_url",
            "overlay_opacity",
            "eyebrow_ar",
            "eyebrow_en",
            "title_ar",
            "title_en",
            "subtitle_ar",
            "subtitle_en",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def _resolve(self, attrs, field):
        if field in attrs:
            return attrs[field]
        return getattr(self.instance, field, "")

    def validate(self, attrs):
        media_type = self._resolve(attrs, "media_type")

        # A hero set to IMAGE or VIDEO with no source renders as an empty band,
        # which looks broken rather than intentional — so it is rejected here
        # instead of failing silently on the site.
        if media_type == HeroMediaChoices.IMAGE and not self._resolve(attrs, "image_url"):
            raise serializers.ValidationError({"image_url": "An image URL is required."})
        if media_type == HeroMediaChoices.VIDEO and not self._resolve(attrs, "video_url"):
            raise serializers.ValidationError({"video_url": "A video URL is required."})
        return attrs

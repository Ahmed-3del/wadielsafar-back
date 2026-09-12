from rest_framework import serializers

from apps.company.models import PromoBar


class PromoBarSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoBar
        fields = (
            "headline_ar",
            "headline_en",
            "code",
            "cta_label_ar",
            "cta_label_en",
            "link",
            "is_active",
            "updated_at",
        )
        read_only_fields = ("updated_at",)

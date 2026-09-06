from rest_framework import serializers

from apps.company.models import Promotion


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = (
            "id",
            "title_ar",
            "title_en",
            "description_ar",
            "description_en",
            "badge_ar",
            "badge_en",
            "code",
            "ends_at",
            "icon",
            "order",
            "is_active",
        )
        read_only_fields = ("id",)

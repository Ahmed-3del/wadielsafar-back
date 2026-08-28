from rest_framework import serializers

from apps.destinations.models import Destination


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = (
            "id",
            "name_ar",
            "name_en",
            "slug",
            "description_ar",
            "description_en",
            "country_ar",
            "country_en",
            "cover_image",
            "is_active",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

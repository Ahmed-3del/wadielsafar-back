from rest_framework import serializers

from apps.services.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "name_ar",
            "name_en",
            "slug",
            "description_ar",
            "description_en",
            "icon",
            "link",
            "service_type",
            "is_on_contact_form",
            "image",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

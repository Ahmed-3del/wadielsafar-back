from rest_framework import serializers

from apps.company.models import Branch


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = (
            "id",
            "name_ar",
            "name_en",
            "phone",
            "phone_display",
            "address_ar",
            "address_en",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

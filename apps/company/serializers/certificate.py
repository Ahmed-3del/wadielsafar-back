from rest_framework import serializers

from apps.company.models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = (
            "id",
            "name_ar",
            "name_en",
            "issuer_ar",
            "issuer_en",
            "reference_number",
            "image",
            "document",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

from rest_framework import serializers

from apps.visas.models import VisaCountry, VisaType
from apps.visas.serializers.visa_country import VisaCountrySerializer


class VisaTypeSerializer(serializers.ModelSerializer):
    country = VisaCountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=VisaCountry.objects.all(), source="country", write_only=True
    )

    class Meta:
        model = VisaType
        fields = (
            "id",
            "country",
            "country_id",
            "name_ar",
            "name_en",
            "purpose",
            "requirements_ar",
            "requirements_en",
            "price",
            "processing_time_days",
            "validity_days",
            "is_active",
        )
        read_only_fields = ("id",)

from rest_framework import serializers

from apps.visas.models import VisaCountry


class VisaCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaCountry
        fields = ("id", "name_ar", "name_en", "flag_image", "is_active")
        read_only_fields = ("id",)

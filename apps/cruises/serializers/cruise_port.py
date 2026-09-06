from rest_framework import serializers

from apps.cruises.models import CruisePort


class CruisePortSerializer(serializers.ModelSerializer):
    class Meta:
        model = CruisePort
        fields = (
            "id",
            "code",
            "name_ar",
            "name_en",
            "city_ar",
            "city_en",
            "country_ar",
            "country_en",
            "country_code",
            "is_popular",
            "is_active",
            "order",
        )
        read_only_fields = ("id",)

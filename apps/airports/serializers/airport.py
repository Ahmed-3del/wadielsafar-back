from rest_framework import serializers

from apps.airports.models import Airport


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "iata_code",
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
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

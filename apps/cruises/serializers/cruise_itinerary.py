from rest_framework import serializers

from apps.cruises.models import CruiseItinerary


class CruiseItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CruiseItinerary
        fields = (
            "id",
            "day_number",
            "port_ar",
            "port_en",
            "description_ar",
            "description_en",
        )
        read_only_fields = ("id",)

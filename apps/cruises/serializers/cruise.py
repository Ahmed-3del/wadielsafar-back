from rest_framework import serializers

from apps.cruises.models import Cruise
from apps.destinations.models import Destination
from apps.destinations.serializers import DestinationSerializer

from .cruise_itinerary import CruiseItinerarySerializer


class CruiseSerializer(serializers.ModelSerializer):
    # Nested for reads so a list response is self-contained; flat id on write.
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.all(),
        source="destination",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Cruise
        fields = (
            "id",
            "title_ar",
            "title_en",
            "slug",
            "cruise_line_ar",
            "cruise_line_en",
            "destination",
            "destination_id",
            "departure_port_ar",
            "departure_port_en",
            "description_ar",
            "description_en",
            "departure_date",
            "duration_nights",
            "price_from",
            "currency",
            "cover_image",
            "included_services_ar",
            "included_services_en",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class CruiseDetailSerializer(CruiseSerializer):
    itinerary = CruiseItinerarySerializer(many=True, read_only=True)

    class Meta(CruiseSerializer.Meta):
        fields = CruiseSerializer.Meta.fields + ("itinerary",)

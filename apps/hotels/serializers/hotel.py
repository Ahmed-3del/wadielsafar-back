from rest_framework import serializers

from apps.destinations.models import Destination
from apps.destinations.serializers import DestinationSerializer
from apps.hotels.models import Hotel, HotelAmenity
from apps.hotels.serializers.hotel_amenity import HotelAmenitySerializer


class HotelSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.all(), source="destination", write_only=True
    )
    amenities = HotelAmenitySerializer(many=True, read_only=True)
    amenity_ids = serializers.PrimaryKeyRelatedField(
        queryset=HotelAmenity.objects.all(),
        source="amenities",
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Hotel
        fields = (
            "id",
            "name_ar",
            "name_en",
            "slug",
            "destination",
            "destination_id",
            "star_rating",
            "address_ar",
            "address_en",
            "description_ar",
            "description_en",
            "amenities",
            "amenity_ids",
            "price_per_night_from",
            "currency",
            "cover_image",
            "check_in_time",
            "check_out_time",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

    def validate_star_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Star rating must be between 1 and 5.")
        return value

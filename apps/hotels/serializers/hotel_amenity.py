from rest_framework import serializers

from apps.hotels.models import HotelAmenity


class HotelAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelAmenity
        fields = ("id", "name_ar", "name_en", "slug", "icon")
        read_only_fields = ("id", "slug")

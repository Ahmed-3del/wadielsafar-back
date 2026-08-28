from rest_framework import serializers

from apps.packages.models import PackageItinerary


class PackageItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageItinerary
        fields = (
            "id",
            "day_number",
            "title_ar",
            "title_en",
            "description_ar",
            "description_en",
        )
        read_only_fields = ("id",)

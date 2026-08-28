from rest_framework import serializers

from apps.destinations.models import Destination
from apps.destinations.serializers import DestinationSerializer
from apps.packages.models import Package, PackageCategory
from apps.packages.serializers.package_category import PackageCategorySerializer
from apps.packages.serializers.package_itinerary import PackageItinerarySerializer


class PackageSerializer(serializers.ModelSerializer):
    # Nested read representation keeps list responses self-contained for the
    # frontends; *_id write-only fields keep create/update payloads flat.
    category = PackageCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=PackageCategory.objects.all(), source="category", write_only=True
    )
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.all(), source="destination", write_only=True
    )

    class Meta:
        model = Package
        fields = (
            "id",
            "title_ar",
            "title_en",
            "slug",
            "category",
            "category_id",
            "destination",
            "destination_id",
            "description_ar",
            "description_en",
            "duration_days",
            "included_services_ar",
            "included_services_en",
            "price_from",
            "cover_image",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class PackageDetailSerializer(PackageSerializer):
    itinerary = PackageItinerarySerializer(many=True, read_only=True)

    class Meta(PackageSerializer.Meta):
        fields = PackageSerializer.Meta.fields + ("itinerary",)

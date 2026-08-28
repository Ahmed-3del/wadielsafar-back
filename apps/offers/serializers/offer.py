from rest_framework import serializers

from apps.offers.models import Offer
from apps.offers.services import OfferService


class OfferSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = (
            "id",
            "title_ar",
            "title_en",
            "slug",
            "description_ar",
            "description_en",
            "service_type",
            "price_before",
            "price_after",
            "discount_percentage",
            "image",
            "starts_at",
            "ends_at",
            "status",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

    def get_status(self, obj):
        return OfferService.compute_status(obj)

    def get_discount_percentage(self, obj):
        return OfferService.compute_discount_percentage(obj)

    def _resolve(self, attrs, field):
        if field in attrs:
            return attrs[field]
        return getattr(self.instance, field, None)

    def validate(self, attrs):
        starts_at = self._resolve(attrs, "starts_at")
        ends_at = self._resolve(attrs, "ends_at")
        price_before = self._resolve(attrs, "price_before")
        price_after = self._resolve(attrs, "price_after")

        if starts_at and ends_at and ends_at < starts_at:
            raise serializers.ValidationError(
                {"ends_at": "End date cannot be before the start date."}
            )
        if price_before is not None and price_after is not None and price_after > price_before:
            raise serializers.ValidationError(
                {"price_after": "Discounted price cannot exceed the original price."}
            )
        return attrs

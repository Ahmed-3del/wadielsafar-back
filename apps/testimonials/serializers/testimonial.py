from rest_framework import serializers

from apps.testimonials.models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = (
            "id",
            "customer_name",
            "customer_title_ar",
            "customer_title_en",
            "content_ar",
            "content_en",
            "rating",
            "avatar_image",
            "service_type",
            "is_approved",
            "is_visible",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

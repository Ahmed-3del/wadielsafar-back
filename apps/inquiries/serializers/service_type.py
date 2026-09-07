from rest_framework import serializers

from apps.inquiries.models import InquiryServiceType


class InquiryServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryServiceType
        fields = ("id", "value", "label_ar", "label_en", "order", "is_active")
        read_only_fields = ("id",)

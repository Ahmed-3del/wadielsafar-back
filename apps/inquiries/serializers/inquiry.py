from django.utils import timezone
from rest_framework import serializers

from apps.destinations.models import Destination
from apps.inquiries.models import Inquiry
from apps.services.models import Service
from common.validators import DATE_ORDER_RULES, parse_iso_date


class InquiryCreateSerializer(serializers.ModelSerializer):
    destination = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.filter(is_active=True), required=False, allow_null=True
    )
    # Only a service the form actually offers. Anything else arriving here is a
    # hand-edited payload, not a visitor.
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True, is_on_contact_form=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Inquiry
        fields = (
            "name",
            "email",
            "phone",
            "service_type",
            "service",
            "destination",
            "travel_date",
            "message",
            "source",
            "details",
        )

    # `details` is written by an unauthenticated public endpoint, so it is
    # bounded here: a flat object of short scalar values. Without this the
    # field is an open door for arbitrary nested payloads.
    MAX_DETAIL_KEYS = 25
    MAX_VALUE_LENGTH = 500

    def validate_travel_date(self, value):
        """A trip that starts before today is a typo, not a lead."""
        if value and value < timezone.localdate():
            raise serializers.ValidationError("Travel date cannot be in the past.")
        return value

    def validate(self, attrs):
        """Order the date pairs inside `details`.

        The forms send these as plain strings, so the model cannot police them.
        A return before its departure reaches an agent as a booking nobody can
        fulfil, and they only find out on the phone.
        """
        details = attrs.get("details") or {}
        today = timezone.localdate()

        for start_key, end_key in DATE_ORDER_RULES:
            start = parse_iso_date(details.get(start_key))
            end = parse_iso_date(details.get(end_key))
            if start and start < today:
                raise serializers.ValidationError(
                    {"details": f"'{start_key}' cannot be in the past."}
                )
            if start and end and end < start:
                raise serializers.ValidationError(
                    {"details": f"'{end_key}' cannot be before '{start_key}'."}
                )
        return attrs

    def validate_details(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Details must be an object.")
        if len(value) > self.MAX_DETAIL_KEYS:
            raise serializers.ValidationError(
                f"Details may contain at most {self.MAX_DETAIL_KEYS} entries."
            )
        cleaned = {}
        for key, item in value.items():
            if not isinstance(item, (str, int, float, bool)) and item is not None:
                raise serializers.ValidationError(f"Detail '{key}' must be a simple value.")
            if isinstance(item, str) and len(item) > self.MAX_VALUE_LENGTH:
                raise serializers.ValidationError(f"Detail '{key}' is too long.")
            cleaned[str(key)[: self.MAX_VALUE_LENGTH]] = item
        return cleaned


class InquirySerializer(serializers.ModelSerializer):
    # Named, not just referenced: the Inquiries list would otherwise show a
    # number where an agent needs to read "Travel Insurance".
    service_name = serializers.CharField(source="service.name_en", read_only=True, default="")

    class Meta:
        model = Inquiry
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "service_type",
            "service",
            "service_name",
            "destination",
            "travel_date",
            "message",
            "status",
            "source",
            "details",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class InquiryStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ("status",)

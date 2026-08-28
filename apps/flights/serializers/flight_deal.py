from rest_framework import serializers

from apps.flights.models import FlightDeal, TripTypeChoices


def _normalize_iata(value):
    code = value.strip().upper()
    if len(code) != 3 or not code.isalpha():
        raise serializers.ValidationError("Enter a 3-letter IATA airport code, e.g. JED.")
    return code


class FlightDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightDeal
        fields = (
            "id",
            "title_ar",
            "title_en",
            "slug",
            "origin_city_ar",
            "origin_city_en",
            "origin_airport_code",
            "destination_city_ar",
            "destination_city_en",
            "destination_airport_code",
            "airline_name_ar",
            "airline_name_en",
            "airline_logo",
            "trip_type",
            "cabin_class",
            "price_from",
            "currency",
            "departure_date",
            "return_date",
            "baggage_allowance_kg",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

    def validate_origin_airport_code(self, value):
        return _normalize_iata(value)

    def validate_destination_airport_code(self, value):
        return _normalize_iata(value)

    def _resolve(self, attrs, field):
        if field in attrs:
            return attrs[field]
        return getattr(self.instance, field, None)

    def validate(self, attrs):
        departure_date = self._resolve(attrs, "departure_date")
        return_date = self._resolve(attrs, "return_date")
        trip_type = self._resolve(attrs, "trip_type") or TripTypeChoices.ROUND_TRIP

        if departure_date and return_date and return_date < departure_date:
            raise serializers.ValidationError(
                {"return_date": "Return date cannot be before the departure date."}
            )
        if trip_type == TripTypeChoices.ROUND_TRIP and departure_date and not return_date:
            raise serializers.ValidationError(
                {"return_date": "A round trip with a departure date requires a return date."}
            )
        return attrs

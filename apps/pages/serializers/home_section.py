from rest_framework import serializers

from apps.pages.models import HomeSection


class HomeSectionSerializer(serializers.ModelSerializer):
    # The human name for the key, so the panel does not have to keep its own
    # copy of the label list.
    label = serializers.CharField(source="get_key_display", read_only=True)

    class Meta:
        model = HomeSection
        fields = ("id", "key", "label", "order", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "label", "created_at", "updated_at")


class HomeSectionReorderSerializer(serializers.Serializer):
    """The whole running order in one request.

    Sending the full list rather than a pair of swapped rows keeps the order
    consistent: two PATCHes can interleave with another editor's and leave two
    sections claiming the same position.
    """

    keys = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    def validate_keys(self, value):
        known = set(HomeSection.objects.values_list("key", flat=True))
        unknown = [key for key in value if key not in known]
        if unknown:
            raise serializers.ValidationError(f"Unknown sections: {', '.join(unknown)}.")
        if len(set(value)) != len(value):
            raise serializers.ValidationError("A section cannot appear twice.")
        return value

from rest_framework import serializers

from apps.navigation.models import NavItem


class NavItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavItem
        fields = (
            "id",
            "label_ar",
            "label_en",
            "href",
            "group",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_href(self, value):
        """Site-relative paths only.

        The front end prefixes the locale and renders these through its own
        Link, so an absolute URL would break routing — and letting an editor
        put an arbitrary host in the header is an open redirect wearing a
        navigation label.
        """
        href = value.strip()
        if not href.startswith("/"):
            raise serializers.ValidationError("Must start with / — for example /packages.")
        if href.startswith("//"):
            raise serializers.ValidationError("Must be a path on this site, not another host.")
        return href

from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Safe fields only — never expose password/is_superuser/permission sets.
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "date_joined",
        )
        read_only_fields = fields

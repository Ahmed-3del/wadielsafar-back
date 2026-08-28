from rest_framework import serializers

from apps.packages.models import PackageCategory


class PackageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCategory
        fields = ("id", "name_ar", "name_en", "slug")
        read_only_fields = ("id", "slug")

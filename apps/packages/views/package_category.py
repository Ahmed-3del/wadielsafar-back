from rest_framework import viewsets

from apps.packages.models import PackageCategory
from apps.packages.permissions import PackagePermission
from apps.packages.serializers import PackageCategorySerializer


class PackageCategoryViewSet(viewsets.ModelViewSet):
    queryset = PackageCategory.objects.all()
    serializer_class = PackageCategorySerializer
    permission_classes = (PackagePermission,)
    lookup_field = "slug"
    search_fields = ("name_ar", "name_en")

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.packages.filters.package_filter import PackageFilter
from apps.packages.models import Package
from apps.packages.permissions import PackagePermission
from apps.packages.serializers import PackageDetailSerializer, PackageSerializer
from apps.packages.services import PackageService
from common.constants import STAFF_CONTENT_ROLES


class PackageViewSet(viewsets.ModelViewSet):
    permission_classes = (PackagePermission,)
    filterset_class = PackageFilter
    search_fields = ("title_ar", "title_en", "description_ar", "description_en")
    ordering_fields = ("price_from", "duration_days", "created_at")
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Package.objects.select_related("category", "destination").prefetch_related(
            "itinerary"
        )
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PackageDetailSerializer
        return PackageSerializer

    @action(detail=False, methods=["get"])
    def featured(self, request):
        limit = int(request.query_params.get("limit", 6))
        packages = PackageService.get_featured(limit=limit)
        serializer = PackageSerializer(packages, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="recompute-duration")
    def recompute_duration(self, request, slug=None):
        package = self.get_object()
        duration_days = PackageService.compute_duration_days(package)
        return Response({"duration_days": duration_days})

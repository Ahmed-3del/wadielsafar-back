from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.pages.models import HomeSection
from apps.pages.permissions import PagePermission
from apps.pages.serializers import HomeSectionReorderSerializer, HomeSectionSerializer
from common.constants import STAFF_CONTENT_ROLES


class HomeSectionViewSet(viewsets.ModelViewSet):
    """The homepage's running order.

    No create and no delete: the set of sections is the set of components the
    site ships, so a row without one would render nothing and a missing row
    would make a section unreachable. Editors reorder and switch off.
    """

    serializer_class = HomeSectionSerializer
    permission_classes = (PagePermission,)
    http_method_names = ("get", "patch", "put", "post", "head", "options")

    def get_queryset(self):
        queryset = HomeSection.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        # A section switched off is gone from the site, but has to stay visible
        # to whoever switched it off — otherwise they cannot switch it back on.
        if not is_content_manager:
            queryset = queryset.filter(is_active=True)
        return queryset

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Sections are fixed; reorder or deactivate them instead."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        serializer = HomeSectionReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        keys = serializer.validated_data["keys"]

        with transaction.atomic():
            sections = {s.key: s for s in HomeSection.objects.select_for_update()}
            for position, key in enumerate(keys):
                sections[key].order = position
            HomeSection.objects.bulk_update(sections.values(), ["order"])

        return Response(HomeSectionSerializer(self.get_queryset(), many=True).data)

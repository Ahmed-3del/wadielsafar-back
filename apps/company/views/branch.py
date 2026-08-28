from apps.company.models import Branch
from apps.company.serializers import BranchSerializer
from apps.company.views.base import PublishedViewSet


class BranchViewSet(PublishedViewSet):
    model = Branch
    serializer_class = BranchSerializer
    search_fields = ("name_ar", "name_en", "phone")
    ordering_fields = ("order", "name_en", "created_at")

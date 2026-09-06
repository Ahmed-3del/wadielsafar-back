from apps.company.models import Promotion
from apps.company.serializers import PromotionSerializer
from apps.company.views.base import PublishedViewSet


class PromotionViewSet(PublishedViewSet):
    model = Promotion
    serializer_class = PromotionSerializer
    search_fields = ("title_ar", "title_en", "code")
    ordering_fields = ("order", "ends_at", "created_at")

from apps.company.models import SocialLink
from apps.company.serializers import SocialLinkSerializer
from apps.company.views.base import PublishedViewSet


class SocialLinkViewSet(PublishedViewSet):
    model = SocialLink
    serializer_class = SocialLinkSerializer
    ordering_fields = ("order", "platform", "created_at")

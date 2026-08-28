from apps.company.models import Certificate
from apps.company.serializers import CertificateSerializer
from apps.company.views.base import PublishedViewSet


class CertificateViewSet(PublishedViewSet):
    model = Certificate
    serializer_class = CertificateSerializer
    search_fields = ("name_ar", "name_en", "issuer_ar", "issuer_en")
    ordering_fields = ("order", "name_en", "created_at")

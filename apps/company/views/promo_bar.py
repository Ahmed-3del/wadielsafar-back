from django.http import Http404
from rest_framework import generics

from apps.company.models import PromoBar
from apps.company.permissions import CompanyPermission
from apps.company.serializers import PromoBarSerializer
from common.constants import STAFF_CONTENT_ROLES


class PromoBarView(generics.RetrieveUpdateAPIView):
    """The single strip pinned across the top of the site.

    No list, no id in the URL: exactly one row exists, created on first
    request if somehow missing, the same way the site only ever has one
    strip to show. A visitor who is not staff never sees it while it is
    switched off — the same discretion every other published row on the site
    gets — so the panel can prepare next month's wording before it is meant
    to go live.
    """

    serializer_class = PromoBarSerializer
    permission_classes = (CompanyPermission,)

    def get_object(self):
        obj = PromoBar.objects.first() or PromoBar.objects.create()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not obj.is_active and not is_content_manager:
            raise Http404
        return obj

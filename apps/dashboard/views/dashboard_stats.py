from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboard.permissions import DashboardPermission
from apps.dashboard.services import DashboardService


class DashboardStatsView(APIView):
    """Single admin-overview payload so the panel does not have to fan out
    across every list endpoint just to render its landing page."""

    permission_classes = (DashboardPermission,)

    def get(self, request):
        return Response(DashboardService.get_stats())

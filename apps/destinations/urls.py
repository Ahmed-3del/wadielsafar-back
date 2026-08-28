from rest_framework.routers import DefaultRouter

from apps.destinations.views import DestinationViewSet

router = DefaultRouter()
router.register("", DestinationViewSet, basename="destination")

urlpatterns = router.urls

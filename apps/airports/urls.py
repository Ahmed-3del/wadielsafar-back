from rest_framework.routers import DefaultRouter

from apps.airports.views import AirportViewSet

router = DefaultRouter()
router.register("", AirportViewSet, basename="airport")

urlpatterns = router.urls

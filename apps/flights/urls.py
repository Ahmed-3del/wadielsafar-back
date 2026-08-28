from rest_framework.routers import DefaultRouter

from apps.flights.views import FlightDealViewSet

router = DefaultRouter()
router.register("", FlightDealViewSet, basename="flight")

urlpatterns = router.urls

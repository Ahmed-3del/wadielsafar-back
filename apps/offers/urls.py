from rest_framework.routers import DefaultRouter

from apps.offers.views import OfferViewSet

router = DefaultRouter()
router.register("", OfferViewSet, basename="offer")

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter

from apps.hotels.views import HotelAmenityViewSet, HotelViewSet

router = DefaultRouter()
# "amenities" must be registered before the empty prefix — otherwise the
# empty-prefix router's `<slug>/` pattern matches "amenities" as a hotel slug
# before Django reaches the amenity-specific patterns.
router.register("amenities", HotelAmenityViewSet, basename="hotel-amenity")
router.register("", HotelViewSet, basename="hotel")

urlpatterns = router.urls

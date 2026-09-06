from rest_framework.routers import DefaultRouter

from apps.cruises.views import CruisePortViewSet, CruiseViewSet

router = DefaultRouter()
# "ports" must be registered before the empty prefix, or the empty-prefix
# router's `<pk>/` pattern matches "ports" as a slug first.
router.register("ports", CruisePortViewSet, basename="cruise-port")
router.register("", CruiseViewSet, basename="cruise")

urlpatterns = router.urls

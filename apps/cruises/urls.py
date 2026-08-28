from rest_framework.routers import DefaultRouter

from apps.cruises.views import CruiseViewSet

router = DefaultRouter()
router.register("", CruiseViewSet, basename="cruise")

urlpatterns = router.urls

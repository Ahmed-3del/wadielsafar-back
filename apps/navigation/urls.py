from rest_framework.routers import DefaultRouter

from apps.navigation.views import NavItemViewSet

router = DefaultRouter()
router.register("", NavItemViewSet, basename="nav-item")

urlpatterns = router.urls

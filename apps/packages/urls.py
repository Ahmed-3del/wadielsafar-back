from rest_framework.routers import DefaultRouter

from apps.packages.views import PackageCategoryViewSet, PackageViewSet

router = DefaultRouter()
router.register("categories", PackageCategoryViewSet, basename="package-category")
router.register("", PackageViewSet, basename="package")

urlpatterns = router.urls

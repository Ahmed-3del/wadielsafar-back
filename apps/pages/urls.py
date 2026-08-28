from rest_framework.routers import DefaultRouter

from apps.pages.views import HomeSectionViewSet, PageHeroViewSet, PageViewSet

router = DefaultRouter()
# "heroes" is registered before the empty prefix: the empty-prefix router's
# `<pk>/` pattern would otherwise swallow it as a page id.
router.register("heroes", PageHeroViewSet, basename="page-hero")
router.register("home-sections", HomeSectionViewSet, basename="home-section")
router.register("", PageViewSet, basename="page")

urlpatterns = router.urls

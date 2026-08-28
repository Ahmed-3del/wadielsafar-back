from rest_framework.routers import DefaultRouter

from apps.visas.views import VisaCountryViewSet, VisaTypeViewSet

router = DefaultRouter()
# "countries" must be registered before the empty prefix — otherwise the
# empty-prefix router's `<pk>/` pattern greedily matches "countries" as a
# pk before Django ever reaches the countries-specific patterns.
router.register("countries", VisaCountryViewSet, basename="visa-country")
router.register("", VisaTypeViewSet, basename="visa-type")

urlpatterns = router.urls

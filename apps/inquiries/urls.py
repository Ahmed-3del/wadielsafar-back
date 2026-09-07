from rest_framework.routers import DefaultRouter

from apps.inquiries.views import (
    InquiryFieldViewSet,
    InquiryServiceTypeViewSet,
    InquiryViewSet,
)

router = DefaultRouter()
# Both named prefixes go before the empty one, or the empty-prefix router reads
# them as inquiry ids.
router.register("fields", InquiryFieldViewSet, basename="inquiry-field")
router.register("service-types", InquiryServiceTypeViewSet, basename="inquiry-service-type")
router.register("", InquiryViewSet, basename="inquiry")

urlpatterns = router.urls

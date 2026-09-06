from rest_framework.routers import DefaultRouter

from apps.inquiries.views import InquiryFieldViewSet, InquiryViewSet

router = DefaultRouter()
# "fields" before the empty prefix, or the empty-prefix router reads it as an
# inquiry id.
router.register("fields", InquiryFieldViewSet, basename="inquiry-field")
router.register("", InquiryViewSet, basename="inquiry")

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter

from apps.inquiries.views import InquiryViewSet

router = DefaultRouter()
router.register("", InquiryViewSet, basename="inquiry")

urlpatterns = router.urls

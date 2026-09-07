from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.inquiries.views import (
    ContactFormServiceView,
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

# Before the router, for the same reason the named prefixes go before the empty
# one: the inquiry detail route would otherwise read "form-services" as an id.
urlpatterns = [
    path("form-services/", ContactFormServiceView.as_view(), name="contact-form-services"),
    *router.urls,
]

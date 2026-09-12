from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.company.views import (
    BranchViewSet,
    CertificateViewSet,
    PromoBarView,
    PromotionViewSet,
    SocialLinkViewSet,
)

router = DefaultRouter()
router.register("certificates", CertificateViewSet, basename="certificate")
router.register("branches", BranchViewSet, basename="branch")
router.register("social-links", SocialLinkViewSet, basename="social-link")
router.register("promotions", PromotionViewSet, basename="promotion")

urlpatterns = [
    # A singleton, not a list: no id to route on, unlike everything above.
    path("promo-bar/", PromoBarView.as_view(), name="promo-bar"),
    *router.urls,
]

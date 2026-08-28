from rest_framework.routers import DefaultRouter

from apps.company.views import BranchViewSet, CertificateViewSet, SocialLinkViewSet

router = DefaultRouter()
router.register("certificates", CertificateViewSet, basename="certificate")
router.register("branches", BranchViewSet, basename="branch")
router.register("social-links", SocialLinkViewSet, basename="social-link")

urlpatterns = router.urls

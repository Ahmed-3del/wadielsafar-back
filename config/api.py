from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("auth/", include("apps.authentication.urls")),
    path("users/", include("apps.users.urls")),
    path("destinations/", include("apps.destinations.urls")),
    path("packages/", include("apps.packages.urls")),
    path("services/", include("apps.services.urls")),
    path("flights/", include("apps.flights.urls")),
    path("airports/", include("apps.airports.urls")),
    path("hotels/", include("apps.hotels.urls")),
    path("visas/", include("apps.visas.urls")),
    path("cruises/", include("apps.cruises.urls")),
    path("offers/", include("apps.offers.urls")),
    path("inquiries/", include("apps.inquiries.urls")),
    path("bookings/", include("apps.bookings.urls")),
    path("testimonials/", include("apps.testimonials.urls")),
    path("partners/", include("apps.partners.urls")),
    path("company/", include("apps.company.urls")),
    path("navigation/", include("apps.navigation.urls")),
    path("pages/", include("apps.pages.urls")),
    path("media/", include("apps.media.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
]

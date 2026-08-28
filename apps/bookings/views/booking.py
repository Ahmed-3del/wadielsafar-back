from rest_framework import viewsets

from apps.bookings.filters.booking_filter import BookingFilter
from apps.bookings.models import Booking
from apps.bookings.permissions import BookingPermission
from apps.bookings.serializers import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (BookingPermission,)
    filterset_class = BookingFilter
    search_fields = ("name",)

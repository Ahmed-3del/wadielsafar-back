import django_filters

from apps.bookings.models import Booking


class BookingFilter(django_filters.FilterSet):
    class Meta:
        model = Booking
        # No filterable fields yet — bookings is a Phase 1 scaffold; extend once
        # real business fields land.
        fields = ()

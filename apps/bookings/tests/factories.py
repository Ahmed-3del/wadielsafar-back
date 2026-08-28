import factory

from apps.bookings.models import Booking


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    name = factory.Sequence(lambda n: f"Booking {n}")

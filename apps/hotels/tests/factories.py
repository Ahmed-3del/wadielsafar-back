import factory

from apps.destinations.tests.factories import DestinationFactory
from apps.hotels.models import Hotel, HotelAmenity


class HotelAmenityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HotelAmenity

    name_ar = factory.Sequence(lambda n: f"مرفق {n}")
    name_en = factory.Sequence(lambda n: f"Amenity {n}")
    icon = "wifi"


class HotelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hotel
        skip_postgeneration_save = True

    name_ar = factory.Sequence(lambda n: f"فندق {n}")
    name_en = factory.Sequence(lambda n: f"Hotel {n}")
    destination = factory.SubFactory(DestinationFactory)
    star_rating = 5
    price_per_night_from = "750.00"
    is_active = True

    @factory.post_generation
    def amenities(self, create, extracted, **kwargs):
        if create and extracted:
            self.amenities.set(extracted)

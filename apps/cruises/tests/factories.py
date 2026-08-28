import factory

from apps.cruises.models import Cruise, CruiseItinerary


class CruiseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cruise

    title_ar = factory.Sequence(lambda n: f"رحلة بحرية {n}")
    title_en = factory.Sequence(lambda n: f"Cruise {n}")
    duration_nights = 5
    price_from = "4500.00"


class CruiseItineraryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CruiseItinerary

    cruise = factory.SubFactory(CruiseFactory)
    day_number = factory.Sequence(lambda n: n + 1)
    port_ar = "ميناء"
    port_en = "Port"

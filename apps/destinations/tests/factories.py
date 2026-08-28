import factory

from apps.destinations.models import Destination


class DestinationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Destination

    name_ar = factory.Sequence(lambda n: f"وجهة {n}")
    name_en = factory.Sequence(lambda n: f"Destination {n}")
    country_ar = "السعودية"
    country_en = "Saudi Arabia"
    is_active = True

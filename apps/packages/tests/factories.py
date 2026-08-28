import factory

from apps.destinations.tests.factories import DestinationFactory
from apps.packages.models import Package, PackageCategory, PackageItinerary


class PackageCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackageCategory

    name_ar = factory.Sequence(lambda n: f"فئة {n}")
    name_en = factory.Sequence(lambda n: f"Category {n}")


class PackageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Package

    title_ar = factory.Sequence(lambda n: f"باقة {n}")
    title_en = factory.Sequence(lambda n: f"Package {n}")
    category = factory.SubFactory(PackageCategoryFactory)
    destination = factory.SubFactory(DestinationFactory)
    duration_days = 3
    price_from = "1500.00"
    is_active = True
    is_featured = False


class PackageItineraryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackageItinerary

    package = factory.SubFactory(PackageFactory)
    day_number = factory.Sequence(lambda n: n + 1)
    title_ar = factory.Sequence(lambda n: f"اليوم {n}")
    title_en = factory.Sequence(lambda n: f"Day {n}")

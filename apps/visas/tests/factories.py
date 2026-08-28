import factory

from apps.visas.models import VisaCountry, VisaType


class VisaCountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VisaCountry

    name_ar = factory.Sequence(lambda n: f"دولة {n}")
    name_en = factory.Sequence(lambda n: f"Country {n}")
    is_active = True


class VisaTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VisaType

    country = factory.SubFactory(VisaCountryFactory)
    name_ar = factory.Sequence(lambda n: f"تأشيرة {n}")
    name_en = factory.Sequence(lambda n: f"Visa {n}")
    price = "300.00"
    processing_time_days = 5
    is_active = True

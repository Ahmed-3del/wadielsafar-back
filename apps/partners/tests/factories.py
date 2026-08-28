import factory

from apps.partners.models import Partner


class PartnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Partner

    name_ar = factory.Sequence(lambda n: f"شريك {n}")
    name_en = factory.Sequence(lambda n: f"Partner {n}")
    logo = "https://cdn.example.com/partner.png"
    is_active = True

import factory

from apps.services.models import Service


class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    name_ar = factory.Sequence(lambda n: f"خدمة {n}")
    name_en = factory.Sequence(lambda n: f"Service {n}")
    icon = "plane"
    is_active = True

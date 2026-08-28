import factory

from apps.inquiries.models import Inquiry
from common.constants import ServiceTypeChoices


class InquiryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inquiry

    name = factory.Sequence(lambda n: f"Traveler {n}")
    email = factory.Sequence(lambda n: f"traveler{n}@example.com")
    phone = "+966501234567"
    service_type = ServiceTypeChoices.PACKAGE
    message = "Interested in a package."

import factory

from apps.testimonials.models import Testimonial
from common.constants import ServiceTypeChoices


class TestimonialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Testimonial

    customer_name = factory.Sequence(lambda n: f"Customer {n}")
    customer_title_ar = "مسافر"
    customer_title_en = "Traveler"
    content_ar = "خدمة ممتازة."
    content_en = "Excellent service."
    rating = 5
    service_type = ServiceTypeChoices.PACKAGE
    is_approved = True
    is_visible = True

import pytest
from django.core.exceptions import ValidationError

from apps.testimonials.models import Testimonial
from apps.testimonials.tests.factories import TestimonialFactory

pytestmark = pytest.mark.django_db


def test_str_includes_customer_and_rating():
    testimonial = TestimonialFactory(customer_name="Sara", rating=4)
    assert str(testimonial) == "Sara (4/5)"


def test_is_approved_defaults_to_false():
    testimonial = Testimonial.objects.create(
        customer_name="Sara", content_ar="جيد", content_en="Good", rating=5
    )
    assert testimonial.is_approved is False
    assert testimonial.is_visible is True


@pytest.mark.parametrize("rating", [0, 6])
def test_rating_outside_one_to_five_fails_model_validation(rating):
    testimonial = TestimonialFactory.build(rating=rating)
    with pytest.raises(ValidationError):
        testimonial.full_clean()


def test_default_ordering_is_order_then_newest():
    first = TestimonialFactory(order=1)
    second = TestimonialFactory(order=0)
    assert list(Testimonial.objects.all()) == [second, first]

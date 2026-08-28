import pytest

from apps.testimonials.services import TestimonialService
from apps.testimonials.tests.factories import TestimonialFactory

pytestmark = pytest.mark.django_db


def test_approve_flips_the_flag_and_persists_it():
    testimonial = TestimonialFactory(is_approved=False)
    TestimonialService.approve(testimonial)
    testimonial.refresh_from_db()
    assert testimonial.is_approved is True


def test_approve_is_idempotent():
    testimonial = TestimonialFactory(is_approved=True)
    assert TestimonialService.approve(testimonial).is_approved is True

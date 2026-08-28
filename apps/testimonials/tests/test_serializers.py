import pytest

from apps.testimonials.serializers import TestimonialSerializer
from apps.testimonials.tests.factories import TestimonialFactory

pytestmark = pytest.mark.django_db


def _payload(**overrides):
    data = {
        "customer_name": "Sara",
        "content_ar": "خدمة ممتازة.",
        "content_en": "Excellent service.",
        "rating": 5,
    }
    data.update(overrides)
    return data


def test_serializer_exposes_contract_fields():
    data = TestimonialSerializer(TestimonialFactory()).data
    for field in ("customer_title_ar", "avatar_image", "service_type", "is_approved", "order"):
        assert field in data


@pytest.mark.parametrize("rating", [0, 6])
def test_rating_outside_one_to_five_is_rejected(rating):
    serializer = TestimonialSerializer(data=_payload(rating=rating))
    assert not serializer.is_valid()
    assert "rating" in serializer.errors


def test_service_type_is_optional():
    serializer = TestimonialSerializer(data=_payload())
    assert serializer.is_valid(), serializer.errors


def test_created_testimonial_is_unapproved_by_default():
    serializer = TestimonialSerializer(data=_payload())
    assert serializer.is_valid(), serializer.errors
    assert serializer.save().is_approved is False

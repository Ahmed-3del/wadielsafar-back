import django_filters

from apps.testimonials.models import Testimonial


class TestimonialFilter(django_filters.FilterSet):
    class Meta:
        model = Testimonial
        fields = ("is_approved", "is_visible", "rating", "service_type")

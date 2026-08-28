from apps.testimonials.models import Testimonial


class TestimonialService:
    @staticmethod
    def approve(testimonial: Testimonial) -> Testimonial:
        if not testimonial.is_approved:
            testimonial.is_approved = True
            testimonial.save(update_fields=["is_approved", "updated_at"])
        return testimonial

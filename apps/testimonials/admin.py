from django.contrib import admin

from apps.testimonials.models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "rating",
        "service_type",
        "is_approved",
        "is_visible",
        "order",
        "created_at",
    )
    list_filter = ("is_approved", "is_visible", "rating", "service_type")
    search_fields = ("customer_name", "content_en", "content_ar")

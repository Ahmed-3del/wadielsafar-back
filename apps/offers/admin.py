from django.contrib import admin

from apps.offers.models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "title_en",
        "service_type",
        "price_before",
        "price_after",
        "starts_at",
        "ends_at",
        "is_featured",
        "is_active",
    )
    list_filter = ("service_type", "is_featured", "is_active")
    search_fields = ("title_en", "title_ar")
    prepopulated_fields = {"slug": ("title_en",)}

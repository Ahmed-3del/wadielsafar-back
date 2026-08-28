from django.contrib import admin

from apps.flights.models import FlightDeal


@admin.register(FlightDeal)
class FlightDealAdmin(admin.ModelAdmin):
    list_display = (
        "title_en",
        "origin_airport_code",
        "destination_airport_code",
        "trip_type",
        "cabin_class",
        "price_from",
        "is_featured",
        "is_active",
    )
    list_filter = ("trip_type", "cabin_class", "is_featured", "is_active")
    search_fields = ("title_en", "title_ar", "origin_city_en", "destination_city_en")
    prepopulated_fields = {"slug": ("title_en",)}

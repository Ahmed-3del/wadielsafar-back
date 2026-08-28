from django.contrib import admin

from apps.hotels.models import Hotel, HotelAmenity


@admin.register(HotelAmenity)
class HotelAmenityAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "icon", "slug")
    search_fields = ("name_en", "name_ar")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = (
        "name_en",
        "destination",
        "star_rating",
        "price_per_night_from",
        "is_featured",
        "is_active",
    )
    list_filter = ("is_active", "is_featured", "star_rating", "destination")
    search_fields = ("name_en", "name_ar", "address_en")
    prepopulated_fields = {"slug": ("name_en",)}
    filter_horizontal = ("amenities",)

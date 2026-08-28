from django.contrib import admin

from apps.airports.models import Airport


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("iata_code", "city_en", "country_en", "is_popular", "is_active")
    list_filter = ("is_active", "is_popular", "country_code")
    search_fields = ("iata_code", "city_en", "city_ar", "name_en", "name_ar")

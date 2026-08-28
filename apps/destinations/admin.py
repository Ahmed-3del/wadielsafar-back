from django.contrib import admin

from apps.destinations.models import Destination


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "country_en", "is_active", "order")
    list_filter = ("is_active", "country_en")
    search_fields = ("name_en", "name_ar", "country_ar", "country_en")
    prepopulated_fields = {"slug": ("name_en",)}

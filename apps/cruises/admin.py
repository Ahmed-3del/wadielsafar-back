from django.contrib import admin

from apps.cruises.models import Cruise, CruiseItinerary


class CruiseItineraryInline(admin.TabularInline):
    model = CruiseItinerary
    extra = 1


@admin.register(Cruise)
class CruiseAdmin(admin.ModelAdmin):
    list_display = ("title_en", "duration_nights", "price_from", "is_featured", "is_active")
    list_filter = ("is_featured", "is_active")
    search_fields = ("title_ar", "title_en")
    inlines = [CruiseItineraryInline]

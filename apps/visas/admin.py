from django.contrib import admin

from apps.visas.models import VisaCountry, VisaType


class VisaTypeInline(admin.TabularInline):
    model = VisaType
    extra = 1


@admin.register(VisaCountry)
class VisaCountryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_ar")
    inlines = (VisaTypeInline,)


@admin.register(VisaType)
class VisaTypeAdmin(admin.ModelAdmin):
    list_display = ("name_en", "country", "price", "processing_time_days", "is_active")
    list_filter = ("is_active", "country")
    search_fields = ("name_en", "name_ar")

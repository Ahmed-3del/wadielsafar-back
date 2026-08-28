from django.contrib import admin

from apps.partners.models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_ar")

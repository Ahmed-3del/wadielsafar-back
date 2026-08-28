from django.contrib import admin

from apps.services.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "icon", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_ar")
    prepopulated_fields = {"slug": ("name_en",)}

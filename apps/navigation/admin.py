from django.contrib import admin

from apps.navigation.models import NavItem


@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ("label_en", "label_ar", "href", "group", "order", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("label_en", "label_ar", "href")

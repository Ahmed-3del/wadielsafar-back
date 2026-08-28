from django.contrib import admin

from apps.packages.models import Package, PackageCategory, PackageItinerary


class PackageItineraryInline(admin.TabularInline):
    model = PackageItinerary
    extra = 1


@admin.register(PackageCategory)
class PackageCategoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "slug")
    search_fields = ("name_en", "name_ar")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "title_en",
        "category",
        "destination",
        "duration_days",
        "price_from",
        "is_featured",
        "is_active",
    )
    list_filter = ("is_active", "is_featured", "category", "destination")
    search_fields = ("title_en", "title_ar")
    prepopulated_fields = {"slug": ("title_en",)}
    inlines = (PackageItineraryInline,)

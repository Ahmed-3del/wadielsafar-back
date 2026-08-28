from django.contrib import admin

from apps.pages.models import Page, PageHero


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(PageHero)
class PageHeroAdmin(admin.ModelAdmin):
    list_display = ("page_key", "media_type", "is_active", "updated_at")
    list_filter = ("media_type", "is_active")
    search_fields = ("page_key", "title_ar", "title_en")

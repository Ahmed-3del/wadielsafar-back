from django.contrib import admin

from apps.media.models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_by", "created_at")
    search_fields = ("alt_text_ar", "alt_text_en")

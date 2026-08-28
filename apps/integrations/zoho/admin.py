from django.contrib import admin

from apps.integrations.zoho.models import ZohoSyncLog


@admin.register(ZohoSyncLog)
class ZohoSyncLogAdmin(admin.ModelAdmin):
    list_display = ("inquiry", "status", "zoho_record_id", "attempts", "created_at")
    list_filter = ("status",)
    search_fields = ("zoho_record_id", "inquiry__email", "inquiry__name")
    readonly_fields = ("created_at", "updated_at")

from django.contrib import admin

from apps.inquiries.models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "service_type", "status", "source", "created_at")
    list_filter = ("status", "service_type", "source")
    search_fields = ("name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")

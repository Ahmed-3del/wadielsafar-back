from django.contrib import admin

from apps.company.models import Branch, Certificate, SocialLink


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("name_en", "issuer_en", "reference_number", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_ar", "reference_number")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name_en", "phone", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name_en", "name_ar", "phone")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "url", "is_active", "order")
    list_filter = ("is_active", "platform")

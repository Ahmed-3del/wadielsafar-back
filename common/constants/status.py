from django.db import models


class ServiceTypeChoices(models.TextChoices):
    FLIGHT = "FLIGHT", "Flight"
    HOTEL = "HOTEL", "Hotel"
    PACKAGE = "PACKAGE", "Package"
    VISA = "VISA", "Visa"
    CRUISE = "CRUISE", "Cruise"
    CORPORATE = "CORPORATE", "Corporate"
    OTHER = "OTHER", "Other"


class InquiryStatusChoices(models.TextChoices):
    NEW = "NEW", "New"
    CONTACTED = "CONTACTED", "Contacted"
    QUALIFIED = "QUALIFIED", "Qualified"
    CONVERTED = "CONVERTED", "Converted"
    CLOSED = "CLOSED", "Closed"


class InquirySourceChoices(models.TextChoices):
    WEBSITE = "WEBSITE", "Website"
    PHONE = "PHONE", "Phone"
    WHATSAPP = "WHATSAPP", "WhatsApp"
    REFERRAL = "REFERRAL", "Referral"
    OTHER = "OTHER", "Other"


class VisaPurposeChoices(models.TextChoices):
    """What a visa is for. The homepage widget asks this before it asks
    anything else, and until now there was nowhere to record the answer."""

    TOURISM = "TOURISM", "Tourism"
    BUSINESS = "BUSINESS", "Business"
    STUDY = "STUDY", "Study"
    UMRAH = "UMRAH", "Umrah"
    OTHER = "OTHER", "Other"


class NavGroupChoices(models.TextChoices):
    """Where a link appears. PRIMARY is the header and the mobile menu;
    SECONDARY is the supporting set that only the footer carries."""

    PRIMARY = "PRIMARY", "Primary"
    SECONDARY = "SECONDARY", "Secondary"


class SocialPlatformChoices(models.TextChoices):
    """Networks the site has a mark for. Adding one here without adding its
    icon to the frontend renders a link with no recognisable badge, so the two
    lists are meant to be changed together."""

    FACEBOOK = "FACEBOOK", "Facebook"
    INSTAGRAM = "INSTAGRAM", "Instagram"
    X = "X", "X"
    TIKTOK = "TIKTOK", "TikTok"
    SNAPCHAT = "SNAPCHAT", "Snapchat"
    YOUTUBE = "YOUTUBE", "YouTube"
    LINKEDIN = "LINKEDIN", "LinkedIn"
    WHATSAPP = "WHATSAPP", "WhatsApp"

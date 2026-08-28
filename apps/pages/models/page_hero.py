from django.core.validators import MaxValueValidator
from django.db import models

from common.utilities import TimeStampedModel


class PageKeyChoices(models.TextChoices):
    """One row per top-level route on the customer site."""

    HOME = "home", "Home"
    DESTINATIONS = "destinations", "Destinations"
    PACKAGES = "packages", "Packages"
    VISAS = "visas", "Visas"
    FLIGHTS = "flights", "Flights"
    HOTELS = "hotels", "Hotels"
    CRUISES = "cruises", "Cruises"
    OFFERS = "offers", "Offers"
    CORPORATE = "corporate", "Corporate"
    ABOUT = "about", "About"
    CONTACT = "contact", "Contact"


class HeroMediaChoices(models.TextChoices):
    NONE = "NONE", "Brand gradient"
    IMAGE = "IMAGE", "Image"
    VIDEO = "VIDEO", "Video"


class PageHero(TimeStampedModel):
    """Editable hero for a page: background media plus optional copy overrides.

    Copy is optional on purpose — when a field is blank the site falls back to
    its own translated string, so an editor can change a background without
    having to re-enter (and keep translated) the headline.
    """

    page_key = models.CharField(max_length=32, choices=PageKeyChoices.choices, unique=True)
    media_type = models.CharField(
        max_length=10, choices=HeroMediaChoices.choices, default=HeroMediaChoices.NONE
    )
    image_url = models.URLField(max_length=500, blank=True)
    video_url = models.URLField(max_length=500, blank=True)
    # Shown while the video loads, and used instead of it on small screens and
    # for visitors who prefer reduced motion.
    poster_url = models.URLField(max_length=500, blank=True)
    # Photography varies wildly in brightness, so the scrim is editable rather
    # than a fixed value — it is the difference between legible and unreadable.
    overlay_opacity = models.PositiveSmallIntegerField(
        default=55, validators=[MaxValueValidator(100)]
    )

    eyebrow_ar = models.CharField(max_length=120, blank=True)
    eyebrow_en = models.CharField(max_length=120, blank=True)
    title_ar = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)
    subtitle_ar = models.TextField(blank=True)
    subtitle_en = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("page_key",)
        verbose_name = "page hero"
        verbose_name_plural = "page heroes"

    def __str__(self):
        return f"{self.get_page_key_display()} ({self.get_media_type_display()})"

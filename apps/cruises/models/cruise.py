from django.db import models

from common.utilities import TimeStampedModel, generate_unique_slug


class Cruise(TimeStampedModel):
    """A cruise offering. Fields follow the client's BRD §6 line for كروزات:
    الوجهات، صور الكروز، مدة الرحلة، خط سير الرحلة، السعر، الخدمات المشمولة."""

    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    cruise_line_ar = models.CharField(max_length=150, blank=True)
    cruise_line_en = models.CharField(max_length=150, blank=True)
    # Nullable: a repositioning or multi-region sailing does not map to one
    # destination record.
    destination = models.ForeignKey(
        "destinations.Destination",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cruises",
    )
    departure_port_ar = models.CharField(max_length=150, blank=True)
    departure_port_en = models.CharField(max_length=150, blank=True)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    # Cruises are sold in nights; days are derived for display rather than
    # stored, so the two can never disagree.
    # Cruises are sold on sail dates, unlike packages, which are quoted for
    # whenever the traveller wants. Nullable so an itinerary can be published
    # before its season's dates are confirmed.
    departure_date = models.DateField(null=True, blank=True)
    duration_nights = models.PositiveIntegerField(default=1)
    price_from = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="SAR")
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    included_services_ar = models.TextField(blank=True)
    included_services_en = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-is_featured", "price_from")

    def __str__(self):
        return self.title_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title_en)
        super().save(*args, **kwargs)


class CruiseItinerary(TimeStampedModel):
    """One port call — the خط سير الرحلة the BRD asks for."""

    cruise = models.ForeignKey("cruises.Cruise", on_delete=models.CASCADE, related_name="itinerary")
    day_number = models.PositiveIntegerField()
    port_ar = models.CharField(max_length=150)
    port_en = models.CharField(max_length=150)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "cruise itineraries"
        ordering = ("cruise", "day_number")
        constraints = [
            models.UniqueConstraint(fields=("cruise", "day_number"), name="unique_cruise_day")
        ]

    def __str__(self):
        return f"{self.cruise.title_en} — day {self.day_number}"

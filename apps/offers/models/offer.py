from django.db import models

from common.constants import ServiceTypeChoices
from common.utilities import TimeStampedModel, generate_unique_slug


class OfferStatusChoices(models.TextChoices):
    """Derived from the validity window rather than stored, so an offer can
    never be left in a status that contradicts its own dates."""

    SCHEDULED = "SCHEDULED", "Scheduled"
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"


class Offer(TimeStampedModel):
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    service_type = models.CharField(max_length=20, choices=ServiceTypeChoices.choices)
    price_before = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_after = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.URLField(max_length=500, blank=True, null=True)
    starts_at = models.DateField()
    ends_at = models.DateField()
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-is_featured", "-starts_at")

    def __str__(self):
        return self.title_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title_en)
        super().save(*args, **kwargs)

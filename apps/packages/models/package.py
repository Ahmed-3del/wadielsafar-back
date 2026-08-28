from django.db import models

from common.utilities import TimeStampedModel, generate_unique_slug


class Package(TimeStampedModel):
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        "packages.PackageCategory", on_delete=models.PROTECT, related_name="packages"
    )
    destination = models.ForeignKey(
        "destinations.Destination", on_delete=models.PROTECT, related_name="packages"
    )
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    # Editable directly, but PackageService.compute_duration_days() can
    # recompute it from the itinerary once days are added.
    duration_days = models.PositiveIntegerField(default=1)
    price_from = models.DecimalField(max_digits=10, decimal_places=2)
    # A URL rather than a stored file: content editors paste a link from the
    # media library (apps/media, which does own real uploads) or a CDN.
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    # الخدمات المشمولة — authored as free text, rendered as a checklist.
    included_services_ar = models.TextField(blank=True)
    included_services_en = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title_en)
        super().save(*args, **kwargs)

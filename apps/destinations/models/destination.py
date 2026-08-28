from django.db import models

from common.utilities import TimeStampedModel, generate_unique_slug


class Destination(TimeStampedModel):
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    country_ar = models.CharField(max_length=100)
    country_en = models.CharField(max_length=100)
    # A URL rather than a stored file: content editors paste a link from the
    # media library (apps/media, which does own real uploads) or a CDN.
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "name_en")

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name_en)
        super().save(*args, **kwargs)

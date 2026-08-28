from django.db import models

from common.utilities import TimeStampedModel, generate_unique_slug


class HotelAmenity(TimeStampedModel):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "hotel amenities"
        ordering = ("name_en",)

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name_en)
        super().save(*args, **kwargs)

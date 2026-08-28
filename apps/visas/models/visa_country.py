from django.db import models

from common.utilities import TimeStampedModel


class VisaCountry(TimeStampedModel):
    name_ar = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    # A URL rather than a stored file: content editors paste a link from the
    # media library (apps/media, which does own real uploads) or a CDN.
    flag_image = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "visa countries"
        ordering = ("name_en",)

    def __str__(self):
        return self.name_en

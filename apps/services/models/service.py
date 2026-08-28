from django.db import models

from common.utilities import TimeStampedModel, generate_unique_slug


class Service(TimeStampedModel):
    name_ar = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    # An icon key (e.g. "plane"), not an asset: both clients own their own
    # icon sets and map the key to their local component.
    icon = models.CharField(max_length=50, blank=True)
    image = models.URLField(max_length=500, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name_en")

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name_en)
        super().save(*args, **kwargs)

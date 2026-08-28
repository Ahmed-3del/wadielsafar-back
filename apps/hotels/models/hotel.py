from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.utilities import TimeStampedModel, generate_unique_slug


class Hotel(TimeStampedModel):
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    destination = models.ForeignKey(
        "destinations.Destination", on_delete=models.PROTECT, related_name="hotels"
    )
    star_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    address_ar = models.CharField(max_length=255, blank=True)
    address_en = models.CharField(max_length=255, blank=True)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    amenities = models.ManyToManyField("hotels.HotelAmenity", related_name="hotels", blank=True)
    price_per_night_from = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="SAR")
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-is_featured", "-star_rating", "name_en")

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name_en)
        self.currency = self.currency.upper()
        super().save(*args, **kwargs)

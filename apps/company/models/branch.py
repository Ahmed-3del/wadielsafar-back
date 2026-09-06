from django.db import models

from common.utilities import TimeStampedModel
from common.validators import phone_validator


class Branch(TimeStampedModel):
    """An office and the line it answers on."""

    name_ar = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    # A dialable number has no spaces and a readable one does, and they are not
    # the same string. Left blank, the frontend prints the dialable form.
    phone_display = models.CharField(max_length=30, blank=True)
    # One line, in reading order: neighbourhood, street, city.
    address_ar = models.CharField(max_length=255, blank=True)
    address_en = models.CharField(max_length=255, blank=True)
    # Drives the mini map and the "view on map" link. Blank hides the map and
    # leaves the address as text, which is better than a pin in the sea.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # The head office, called out with a border and a badge. Exactly one is
    # expected; nothing breaks if there are none.
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "branches"
        ordering = ("order", "name_en")

    def __str__(self):
        return f"{self.name_en} ({self.phone})"

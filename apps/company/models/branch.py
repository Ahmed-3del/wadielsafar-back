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
    # A photo of the office — the storefront or the desk, usually. Blank
    # shows the map preview in its place instead of an empty frame.
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    # Free text rather than a per-day schedule — "Sat–Thu: 9am–9pm · Fri:
    # Closed" fits a branch card in one line, where a table of seven rows
    # would not. Blank hides the row rather than printing empty hours.
    working_hours_ar = models.CharField(max_length=200, blank=True)
    working_hours_en = models.CharField(max_length=200, blank=True)
    # Drives the mini map and the "view on map" link. Blank hides the map and
    # leaves the address as text, which is better than a pin in the sea.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # This branch's own listing, pasted from Google Maps' Share button — the
    # coordinates above can only ever open a search, which is a pin labelled
    # with a lat/lng string, not the branch's real name, photo and reviews.
    # Blank falls back to searching by name and address instead.
    google_maps_url = models.URLField(max_length=500, blank=True)
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

from django.db import models

from common.utilities import TimeStampedModel, normalize_arabic, normalize_latin


class CruisePort(TimeStampedModel):
    """A port ships sail from, for the homepage's cruise search.

    Reference data, like apps.airports: these ports exist in the world, and a
    row here claims nothing about sailings the company sells, prices, or cruise
    line relationships. An agent can still switch one off — a port nobody books
    through is noise in a dropdown.

    The search asks for a country first and a port second, so the country
    columns are what group the list rather than decoration on it.
    """

    # The natural key, so a re-seed updates in place instead of duplicating.
    # A slug rather than a code: cruise ports have no IATA equivalent that
    # travellers would recognise.
    code = models.SlugField(max_length=60, unique=True, db_index=True)
    # The port itself — "Port Rashid", "Civitavecchia". Often not the city name,
    # which is why both are stored.
    name_ar = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    city_ar = models.CharField(max_length=120)
    city_en = models.CharField(max_length=120)
    country_ar = models.CharField(max_length=120)
    country_en = models.CharField(max_length=120)
    # ISO 3166-1 alpha-2. Groups the ports under a country and draws its flag;
    # storing the flag itself would put presentation in the database.
    country_code = models.CharField(max_length=2, blank=True)
    # What the picker offers before anyone has typed: where this market sails
    # from, and the home ports its travellers fly out to join.
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    # Folded copies of the Arabic, maintained by save(). Someone hunting for
    # إسطنبول types "اسطنبول"; matching the stored spelling literally would find
    # nothing on an Arabic-first site. Never displayed — see
    # common.utilities.arabic.
    city_ar_folded = models.CharField(max_length=120, blank=True, db_index=True)
    text_ar_folded = models.CharField(max_length=400, blank=True)

    # And the Latin side, for the same reason: the catalogue says Kuşadası,
    # Ålesund and Valparaíso, and nobody searching types the accents.
    city_en_folded = models.CharField(max_length=120, blank=True, db_index=True)
    text_en_folded = models.CharField(max_length=400, blank=True)

    class Meta:
        ordering = ("-is_popular", "order", "country_en", "city_en")
        indexes = [
            models.Index(fields=("country_code",)),
            models.Index(fields=("city_en",)),
        ]

    def __str__(self):
        return f"{self.city_en} — {self.name_en}"

    def save(self, *args, **kwargs):
        self.country_code = self.country_code.upper()
        self.city_ar_folded = normalize_arabic(self.city_ar)
        self.text_ar_folded = normalize_arabic(f"{self.name_ar} {self.country_ar}")
        self.city_en_folded = normalize_latin(self.city_en)
        self.text_en_folded = normalize_latin(f"{self.name_en} {self.country_en}")
        super().save(*args, **kwargs)

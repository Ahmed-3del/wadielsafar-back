from django.db import models

from apps.flights.models.flight_deal import iata_code_validator
from common.utilities import TimeStampedModel, normalize_arabic


class Airport(TimeStampedModel):
    """A searchable airport, used to fill the departure/arrival pickers.

    This is reference data, not content: the rows describe airports that exist
    in the world, and carry no claim about routes the company sells, prices, or
    airline relationships. An agent can still switch one off — a code the
    company never books through is noise in a dropdown.
    """

    # The natural key. Unique so a re-seed updates in place instead of
    # duplicating, and indexed because the picker looks codes up on every
    # keystroke.
    iata_code = models.CharField(
        max_length=3, unique=True, db_index=True, validators=[iata_code_validator]
    )
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    city_ar = models.CharField(max_length=120)
    city_en = models.CharField(max_length=120)
    country_ar = models.CharField(max_length=120)
    country_en = models.CharField(max_length=120)
    # ISO 3166-1 alpha-2. The frontend turns it into a flag; storing the flag
    # itself would put presentation in the database.
    country_code = models.CharField(max_length=2, blank=True)
    # What the picker offers before anyone has typed anything. Saudi departure
    # points and the routes travellers here actually ask for.
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    # Folded copies of the Arabic text, maintained by save(). Someone hunting
    # for إسطنبول types "اسطنبول", and matching the stored spelling literally
    # would find nothing — on an Arabic-first site, most of the time. Never
    # displayed; see common.utilities.arabic.
    city_ar_folded = models.CharField(max_length=120, blank=True, db_index=True)
    text_ar_folded = models.CharField(max_length=400, blank=True)

    class Meta:
        ordering = ("-is_popular", "order", "city_en", "iata_code")
        indexes = [
            models.Index(fields=("city_en",)),
            models.Index(fields=("city_ar",)),
        ]

    def __str__(self):
        return f"{self.iata_code} — {self.city_en}"

    def save(self, *args, **kwargs):
        self.iata_code = self.iata_code.upper()
        self.country_code = self.country_code.upper()
        self.city_ar_folded = normalize_arabic(self.city_ar)
        self.text_ar_folded = normalize_arabic(f"{self.name_ar} {self.country_ar}")
        super().save(*args, **kwargs)

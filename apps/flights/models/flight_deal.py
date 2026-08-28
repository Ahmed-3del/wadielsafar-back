from django.core.validators import RegexValidator
from django.db import models

from common.utilities import TimeStampedModel, generate_unique_slug


class TripTypeChoices(models.TextChoices):
    ONE_WAY = "ONE_WAY", "One way"
    ROUND_TRIP = "ROUND_TRIP", "Round trip"
    MULTI_CITY = "MULTI_CITY", "Multi city"


class CabinClassChoices(models.TextChoices):
    ECONOMY = "ECONOMY", "Economy"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY", "Premium economy"
    BUSINESS = "BUSINESS", "Business"
    FIRST = "FIRST", "First"


# Case-insensitive so a lowercase code from a form/import is normalized by
# save() rather than rejected outright.
iata_code_validator = RegexValidator(
    regex=r"^[A-Za-z]{3}$",
    message="Enter a 3-letter IATA airport code, e.g. JED.",
)


class FlightDeal(TimeStampedModel):
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    origin_city_ar = models.CharField(max_length=100)
    origin_city_en = models.CharField(max_length=100)
    origin_airport_code = models.CharField(max_length=3, validators=[iata_code_validator])
    destination_city_ar = models.CharField(max_length=100)
    destination_city_en = models.CharField(max_length=100)
    destination_airport_code = models.CharField(max_length=3, validators=[iata_code_validator])
    airline_name_ar = models.CharField(max_length=120, blank=True)
    airline_name_en = models.CharField(max_length=120, blank=True)
    airline_logo = models.URLField(max_length=500, blank=True, null=True)
    trip_type = models.CharField(
        max_length=20, choices=TripTypeChoices.choices, default=TripTypeChoices.ROUND_TRIP
    )
    cabin_class = models.CharField(
        max_length=20, choices=CabinClassChoices.choices, default=CabinClassChoices.ECONOMY
    )
    price_from = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="SAR")
    departure_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    baggage_allowance_kg = models.PositiveIntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-is_featured", "price_from")

    def __str__(self):
        return f"{self.origin_airport_code} → {self.destination_airport_code} ({self.title_en})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title_en)
        self.origin_airport_code = self.origin_airport_code.upper()
        self.destination_airport_code = self.destination_airport_code.upper()
        self.currency = self.currency.upper()
        super().save(*args, **kwargs)

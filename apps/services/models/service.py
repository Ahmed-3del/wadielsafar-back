from django.db import models

from common.utilities import TimeStampedModel, generate_unique_slug
from common.validators import validate_internal_path


class ServiceIconChoices(models.TextChoices):
    """The marks the website can draw for a service.

    A free-text key looked more flexible and was not: whoever filled it in had
    no way to know which words the site recognises, and an unknown one fell
    back to a generic ticket without saying so. The list is deliberately wider
    than the services shipped today, so there is room to add one without a
    deployment — but every key here is drawn by the site.
    """

    CAR = "car", "Car"
    TRANSFER = "transfer", "Airport shuttle"
    LICENCE = "licence", "Driving licence"
    SHIELD = "shield", "Shield (insurance)"
    SIM = "sim", "SIM card"
    TICKET = "ticket", "Ticket"
    PASSPORT = "passport", "Passport"
    HEADSET = "headset", "Headset (support)"
    PLANE = "plane", "Aeroplane"
    BED = "bed", "Bed (hotel)"
    SHIP = "ship", "Ship (cruise)"
    GLOBE = "globe", "Globe"
    BAG = "bag", "Luggage"
    MAP = "map", "Map"
    PIN = "pin", "Map pin"
    CALENDAR = "calendar", "Calendar"
    CLOCK = "clock", "Clock"
    USERS = "users", "People"
    MEAL = "meal", "Meal"
    TAG = "tag", "Price tag"
    GIFT = "gift", "Gift"
    BOOK = "book", "Book (study)"
    MOSQUE = "mosque", "Mosque (Umrah)"


class Service(TimeStampedModel):
    name_ar = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    # A key, not an asset: the clients own their own icon sets and map the key
    # to their local component. Constrained to what the website actually draws,
    # so the panel can offer the list rather than ask for a guess.
    icon = models.CharField(max_length=50, choices=ServiceIconChoices.choices, blank=True)
    image = models.URLField(max_length=500, blank=True, null=True)
    # Where the tile leads. Blank sends the reader to the contact form, which
    # is the right answer for most of these — but an "Instant visa" tile
    # belongs on /visas, and that was not something an editor could say.
    link = models.CharField(max_length=200, blank=True, validators=[validate_internal_path])
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

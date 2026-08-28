from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.constants import ServiceTypeChoices
from common.utilities import TimeStampedModel


class Testimonial(TimeStampedModel):
    customer_name = models.CharField(max_length=120)
    customer_title_ar = models.CharField(max_length=120, blank=True)
    customer_title_en = models.CharField(max_length=120, blank=True)
    content_ar = models.TextField()
    content_en = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    avatar_image = models.URLField(max_length=500, blank=True, null=True)
    service_type = models.CharField(
        max_length=20, choices=ServiceTypeChoices.choices, blank=True, null=True
    )
    # Moderation gate: nothing reaches the public site until a staff member
    # approves it, so this defaults to False and only staff can flip it.
    is_approved = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "-created_at")

    def __str__(self):
        return f"{self.customer_name} ({self.rating}/5)"

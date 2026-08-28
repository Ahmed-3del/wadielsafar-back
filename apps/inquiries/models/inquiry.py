from django.db import models

from common.constants import InquirySourceChoices, InquiryStatusChoices, ServiceTypeChoices
from common.utilities import TimeStampedModel
from common.validators import phone_validator


class Inquiry(TimeStampedModel):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, validators=[phone_validator])
    service_type = models.CharField(max_length=20, choices=ServiceTypeChoices.choices)
    # Nullable: a general/corporate inquiry may not be tied to one destination.
    destination = models.ForeignKey(
        "destinations.Destination",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiries",
    )
    travel_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=InquiryStatusChoices.choices, default=InquiryStatusChoices.NEW
    )
    source = models.CharField(
        max_length=20,
        choices=InquirySourceChoices.choices,
        default=InquirySourceChoices.WEBSITE,
    )
    # Service-specific request data (route and cabin for a flight, dates and
    # room count for a hotel, and so on). Kept as JSON rather than columns per
    # service because the shape differs per service_type and support only ever
    # reads it back as a labelled list.
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name_plural = "inquiries"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} ({self.service_type})"

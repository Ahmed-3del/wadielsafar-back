from django.db import models

from common.utilities import TimeStampedModel


class ZohoSyncStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    # Recorded when credentials are absent, so "we never tried" stays
    # distinguishable from "we tried and it failed".
    SKIPPED = "SKIPPED", "Skipped"


class ZohoSyncLog(TimeStampedModel):
    inquiry = models.ForeignKey(
        "inquiries.Inquiry", on_delete=models.CASCADE, related_name="zoho_syncs"
    )
    status = models.CharField(
        max_length=20, choices=ZohoSyncStatusChoices.choices, default=ZohoSyncStatusChoices.PENDING
    )
    zoho_record_id = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Inquiry {self.inquiry_id} → {self.status}"

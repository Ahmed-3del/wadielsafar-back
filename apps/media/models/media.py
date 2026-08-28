from django.conf import settings
from django.db import models

from common.utilities import TimeStampedModel


class Media(TimeStampedModel):
    file = models.FileField(upload_to="library/%Y/%m/")
    alt_text_ar = models.CharField(max_length=255, blank=True)
    alt_text_en = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploads"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.file.name

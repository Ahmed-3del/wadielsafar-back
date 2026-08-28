from django.db import models

from common.utilities import TimeStampedModel


class Booking(TimeStampedModel):
    # Minimal scaffold field only — full business fields land in a later phase.
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

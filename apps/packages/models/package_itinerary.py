from django.db import models

from common.utilities import TimeStampedModel


class PackageItinerary(TimeStampedModel):
    package = models.ForeignKey(
        "packages.Package", on_delete=models.CASCADE, related_name="itinerary"
    )
    day_number = models.PositiveIntegerField()
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "package itineraries"
        ordering = ("package", "day_number")
        constraints = [
            models.UniqueConstraint(fields=("package", "day_number"), name="unique_day_per_package")
        ]

    def __str__(self):
        return f"{self.package.title_en} - Day {self.day_number}"

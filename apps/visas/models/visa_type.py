from django.db import models

from common.constants import VisaEntryChoices, VisaPurposeChoices
from common.utilities import TimeStampedModel


class VisaType(TimeStampedModel):
    country = models.ForeignKey(
        "visas.VisaCountry", on_delete=models.CASCADE, related_name="visa_types"
    )
    name_ar = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    # Blank rather than defaulted to tourism: an unlabelled visa type should
    # show up under every purpose, not be silently filed under the wrong one.
    purpose = models.CharField(
        max_length=20, choices=VisaPurposeChoices.choices, blank=True
    )
    # Blank rather than defaulted: for some visas it depends on the
    # applicant, and guessing sends someone to an embassy for nothing.
    entry_type = models.CharField(
        max_length=10, choices=VisaEntryChoices.choices, blank=True
    )
    # Overrides the country photo for one visa — an Umrah visa wants Makkah,
    # not a skyline. Blank falls back to the country's own image.
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    requirements_ar = models.TextField(blank=True)
    requirements_en = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    processing_time_days = models.PositiveIntegerField()
    # مدة الصلاحية — nullable because it varies by applicant for some visas and
    # a wrong number here is worse than none.
    validity_days = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("country", "name_en")

    def __str__(self):
        return f"{self.country.name_en} - {self.name_en}"

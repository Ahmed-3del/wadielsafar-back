from django.db import models

from common.constants import ServiceTypeChoices
from common.utilities import TimeStampedModel


class InquiryServiceType(TimeStampedModel):
    """One entry in the "what do you need?" list on the contact form.

    The values are fixed — they are the column every enquiry is filed under and
    the panel filters by, so inventing one would produce enquiries nothing can
    read. What an editor owns is everything a visitor sees: the wording, the
    order, and whether it is offered at all.
    """

    value = models.CharField(max_length=20, choices=ServiceTypeChoices.choices, unique=True)
    label_ar = models.CharField(max_length=80)
    label_en = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    # Switched off disappears from the form. Enquiries already filed under it
    # keep their value, and the panel keeps showing them.
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "value")

    def __str__(self):
        return self.label_en

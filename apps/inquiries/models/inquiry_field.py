from django.core.exceptions import ValidationError
from django.db import models

from common.constants import ServiceTypeChoices
from common.utilities import TimeStampedModel


class InquiryFieldTypeChoices(models.TextChoices):
    """What the website renders for this question."""

    TEXT = "TEXT", "Short text"
    TEXTAREA = "TEXTAREA", "Long text"
    NUMBER = "NUMBER", "Number"
    DATE = "DATE", "Date"
    SELECT = "SELECT", "Choice from a list"


def split_options(text: str) -> list[str]:
    """One option per line, blank lines ignored."""
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


class InquiryField(TimeStampedModel):
    """One extra question on the contact form, for one service.

    The contact form asks name, email, phone and a message whatever the
    service — but what an agent needs beyond that differs, and used to be
    fixed in the website's code. These rows are that difference, so the
    questions asked of a cruise enquiry can change without a deployment.

    The answer is filed in `Inquiry.details` under `key`, which is why the key
    is a slug and unique per service: it is a column name in everything that
    reads an inquiry back.
    """

    service_type = models.CharField(max_length=20, choices=ServiceTypeChoices.choices)
    key = models.SlugField(max_length=40)
    label_ar = models.CharField(max_length=120)
    label_en = models.CharField(max_length=120)
    field_type = models.CharField(
        max_length=10,
        choices=InquiryFieldTypeChoices.choices,
        default=InquiryFieldTypeChoices.TEXT,
    )
    placeholder_ar = models.CharField(max_length=160, blank=True)
    placeholder_en = models.CharField(max_length=160, blank=True)
    # One option per line, the two languages read in step. Two text boxes
    # rather than a second table: an editor adding "Business class" should not
    # have to visit another screen to do it.
    options_ar = models.TextField(blank=True)
    options_en = models.TextField(blank=True)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("service_type", "order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("service_type", "key"),
                name="unique_inquiry_field_key_per_service",
            )
        ]

    def __str__(self):
        return f"{self.get_service_type_display()} — {self.label_en}"

    def clean(self):
        """A choice list has to be a list, and the two languages have to line up.

        They are zipped by position when the website renders them, so a missing
        line in one language would put an Arabic label on an English answer.
        """
        if self.field_type != InquiryFieldTypeChoices.SELECT:
            return

        arabic = split_options(self.options_ar)
        english = split_options(self.options_en)
        if not arabic or not english:
            raise ValidationError(
                {"options_en": "A choice field needs its options, one per line, in both languages."}
            )
        if len(arabic) != len(english):
            raise ValidationError(
                {
                    "options_en": (
                        f"Both languages need the same number of options — "
                        f"{len(arabic)} in Arabic, {len(english)} in English."
                    )
                }
            )

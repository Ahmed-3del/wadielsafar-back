from django.db import models

from common.utilities import TimeStampedModel
from common.validators import validate_internal_path


class PromotionIconChoices(models.TextChoices):
    """The mark on the card. Three, because there are three shapes of saving:
    a discount, a deadline, and a reward for bringing someone."""

    TAG = "TAG", "Discount tag"
    CLOCK = "CLOCK", "Countdown"
    GIFT = "GIFT", "Referral gift"


class Promotion(TimeStampedModel):
    """One card in the "ways to save" row on the homepage.

    Every figure on these cards is a commercial commitment — a percentage, a
    code, a deadline — so none of them are written into the site. They live
    here, where whoever is running the offer can change or end it without a
    deployment.
    """

    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    # The figure the card leads with — "15%", "10%", "SAR 200". Free text
    # rather than a number: a saving is not always a percentage.
    badge_ar = models.CharField(max_length=40, blank=True)
    badge_en = models.CharField(max_length=40, blank=True)
    # Shown as something to copy when set. Blank means the offer applies
    # without one.
    code = models.CharField(max_length=30, blank=True)
    # Drives the live countdown. Blank means the offer has no announced end,
    # and the card shows no timer rather than an invented one.
    ends_at = models.DateTimeField(null=True, blank=True)
    icon = models.CharField(
        max_length=10, choices=PromotionIconChoices.choices, default=PromotionIconChoices.TAG
    )
    # Where "claim this offer" leads. Blank sends the reader to the contact
    # form carrying the code, which is the right answer for an offer an agent
    # applies by hand — but an offer tied to one page should lead there.
    link = models.CharField(max_length=200, blank=True, validators=[validate_internal_path])
    # The words on the button. Blank uses the site's own wording, so an editor
    # only fills this in when this offer needs its own call to action.
    cta_label_ar = models.CharField(max_length=60, blank=True)
    cta_label_en = models.CharField(max_length=60, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.title_en

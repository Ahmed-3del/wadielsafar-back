from django.db import models

from common.utilities import TimeStampedModel
from common.validators import validate_internal_path


class PromoBar(TimeStampedModel):
    """The single strip pinned across the top of every page.

    Exactly one row is ever read or written — see PromoBarView, which always
    resolves to it rather than looking one up by id, the same way there is
    only ever one strip live on the site to match. is_active is how an editor
    pauses the offer without losing today's wording, since the same seasonal
    code tends to come back.
    """

    headline_ar = models.CharField(max_length=200)
    headline_en = models.CharField(max_length=200)
    # Shown as something to copy, in a chip of its own. Blank hides the chip
    # entirely — not every offer needs a code to quote.
    code = models.CharField(max_length=32, blank=True)
    cta_label_ar = models.CharField(max_length=60)
    cta_label_en = models.CharField(max_length=60)
    # Blank falls back to the contact form, same as leaving a Promotion's own
    # link blank.
    link = models.CharField(
        max_length=200, blank=True, default="/contact", validators=[validate_internal_path]
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "promo bar"
        verbose_name_plural = "promo bar"

    def __str__(self):
        return self.headline_en or "Promo bar"

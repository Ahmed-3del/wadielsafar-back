from django.db import models

from common.utilities import TimeStampedModel


class Certificate(TimeStampedModel):
    """An official licence or registration the company can actually show.

    Every field here is supplied by the company. Nothing is inferred and
    nothing is generated: a government mark the company has not handed over is
    a claim the site cannot support, so an empty table renders an empty row
    rather than a placeholder badge.
    """

    name_ar = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    # The issuing body, shown under the badge — "وزارة التجارة".
    issuer_ar = models.CharField(max_length=150, blank=True)
    issuer_en = models.CharField(max_length=150, blank=True)
    # The registration/licence number, if it is one worth printing.
    reference_number = models.CharField(max_length=60, blank=True)
    # The badge artwork shown in the footer. A URL like every other image field
    # here: editors paste a link from the media library or upload into it.
    image = models.URLField(max_length=500, blank=True, null=True)
    # What opens when a visitor taps the badge. A PDF in the media library, or
    # a link to the issuing authority's own verification page. Blank means the
    # badge is shown but is not clickable, which is better than a dead link.
    document = models.URLField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name_en")

    def __str__(self):
        return self.name_en

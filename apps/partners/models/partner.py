from django.db import models

from common.utilities import TimeStampedModel


class Partner(TimeStampedModel):
    """An airline, hotel group, cruise line or authority the company works with.

    Logos only — no claim about the nature of the relationship is made here,
    because the site has no way to substantiate one and the wrong word is a
    commercial problem rather than a copy problem.
    """

    name_ar = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    # A URL rather than a stored file, matching every other image field here:
    # editors paste a link from the media library or upload into it directly.
    logo = models.URLField(max_length=500, blank=True, null=True)
    # Optional: plenty of partners have no site worth linking to, and a dead
    # link on a logo wall is worse than no link.
    website_url = models.URLField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name_en")

    def __str__(self):
        return self.name_en

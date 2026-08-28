from django.db import models

from common.constants import SocialPlatformChoices
from common.utilities import TimeStampedModel


class SocialLink(TimeStampedModel):
    """One profile the company keeps.

    The platform is chosen, not guessed from the URL. Matching on the hostname
    meant a shortened or vanity domain rendered as no icon at all, and the
    person adding the link had no way to say which network it was.
    """

    platform = models.CharField(max_length=20, choices=SocialPlatformChoices.choices)
    url = models.URLField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "platform")

    def __str__(self):
        return f"{self.get_platform_display()} — {self.url}"

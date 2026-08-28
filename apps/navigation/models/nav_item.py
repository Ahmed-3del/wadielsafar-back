from django.db import models

from common.constants import NavGroupChoices
from common.utilities import TimeStampedModel


class NavItem(TimeStampedModel):
    """One link in the site's navigation.

    Labels are stored rather than looked up from the translation files, because
    an editor adding a link has no way to add a message key — the whole point of
    making this editable is that it does not need a deploy.
    """

    label_ar = models.CharField(max_length=150)
    label_en = models.CharField(max_length=150)
    # Site-relative, without the locale prefix: the front end adds /ar or /en.
    href = models.CharField(max_length=200)
    group = models.CharField(
        max_length=20, choices=NavGroupChoices.choices, default=NavGroupChoices.PRIMARY
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("group", "order", "id")

    def __str__(self):
        return f"{self.label_en} ({self.href})"

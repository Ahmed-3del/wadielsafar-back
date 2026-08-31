"""Guard for the demo seeders.

Every `seed_demo_*` command overwrites the rows it owns. In development that
is the point; anywhere else those rows are somebody's real content, so getting
past this takes an explicit flag.
"""

from django.conf import settings
from django.core.management.base import CommandError

UNSPLASH = "https://images.unsplash.com/photo-{}?w=1600&q=80"


def photo(photo_id: str) -> str:
    """A demo image URL, or "" when there is no photo for this row.

    Every id the seeders use was opened and looked at, not just checked for a
    200: a photo of skiers filed under Jeddah is worse than no photo. Where
    none could be sourced the field is left empty, and the site draws its own
    brand-coloured block — see MediaImage, which prefers that to an
    unpredictable third-party picture.

    Returning "" for an empty id rather than a URL with no id in it is what
    makes that fallback actually fire; `photo-?w=1600` is a truthy string and
    a 404.
    """
    return UNSPLASH.format(photo_id) if photo_id else ""


def guard_demo_write(force: bool) -> None:
    if not settings.DEBUG and not force:
        raise CommandError(
            "DEBUG is off. The demo seeders overwrite content — "
            "re-run with --force if that is genuinely what you want."
        )

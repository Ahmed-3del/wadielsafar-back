from django.core.exceptions import ValidationError


def validate_internal_path(value: str) -> None:
    """Where a link on the website leads. Site-relative only.

    The website renders these through its localised Link, which prefixes the
    language — an absolute URL would come out as /ar/https://example.com.

    Shared by anything an editor can point somewhere: service tiles, promotion
    buttons, and whatever comes next.
    """
    if value and not value.startswith("/"):
        raise ValidationError("Start the link with / — it is a path on this site, e.g. /visas.")

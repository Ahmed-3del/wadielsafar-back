"""Date sanity checks shared by the public forms.

A trip cannot start yesterday and cannot come back before it left. The website
enforces both, but the website is not the only way to reach the API, so the
rules live here too.
"""

from datetime import date

# Pairs inside an inquiry's `details` where the second value must not fall
# before the first. Both come from the request forms: flights ask for a
# departure and a return, hotels for a check-in and a check-out.
DATE_ORDER_RULES: tuple[tuple[str, str], ...] = (
    ("depart", "return"),
    ("check_in", "check_out"),
)


def parse_iso_date(value: object) -> date | None:
    """The ISO date in `value`, or None if it is not one.

    `details` is free-form, so anything that is not a date is simply not our
    business here — returning None lets the caller skip the check rather than
    reject a field it does not own.
    """
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None

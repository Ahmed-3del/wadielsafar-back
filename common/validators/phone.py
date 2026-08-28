from django.core.validators import RegexValidator

# Loose international format (+ and 7-15 digits) rather than Saudi-only,
# since inquiries may come from travelers outside KSA.
phone_validator = RegexValidator(
    regex=r"^\+?[1-9]\d{6,14}$",
    message="Enter a valid phone number in international format, e.g. +966501234567.",
)

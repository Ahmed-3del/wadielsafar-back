from django.core.management.base import BaseCommand

from apps.inquiries.models import InquiryServiceType

# The list the contact form offers, in the order it offers it. The values are
# the enquiry's own column and cannot change; the wording and the order are an
# editor's to arrange, which is why they live in rows rather than in the site.
SERVICE_TYPES = [
    ("FLIGHT", "طيران", "Flight"),
    ("HOTEL", "فندق", "Hotel"),
    ("PACKAGE", "باقة سياحية", "Package"),
    ("VISA", "تأشيرة", "Visa"),
    ("CRUISE", "رحلة بحرية", "Cruise"),
    ("CORPORATE", "سفر الشركات", "Corporate Travel"),
    ("OTHER", "أخرى", "Other"),
]


class Command(BaseCommand):
    help = "Load the contact form's service list. Safe to re-run."

    def handle(self, *args, **options):
        created = updated = 0
        for order, (value, label_ar, label_en) in enumerate(SERVICE_TYPES):
            _, was_created = InquiryServiceType.objects.update_or_create(
                value=value,
                defaults={
                    "label_ar": label_ar,
                    "label_en": label_en,
                    "order": order,
                    "is_active": True,
                },
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(
            self.style.SUCCESS(f"Contact form services: {created} created, {updated} refreshed.")
        )

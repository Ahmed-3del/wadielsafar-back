"""Demo offers.

Demonstration content. The prices and the discounts here are ours and are
meant to be replaced.

Validity windows are generated relative to today, so a re-run never leaves the
homepage advertising an offer that expired months ago — and one row starts in
the future on purpose, so the panel's SCHEDULED state has something in it.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.offers.models import Offer
from common.utilities import guard_demo_write, photo

# slug, title_ar, title_en, service, before, after, photo id,
# starts (days from today), ends (days from today), featured, desc_ar, desc_en
# One record per row. `ruff format` gives every field its own line and turns a
# readable table into column soup; the project lints with `ruff check`.
# fmt: off
OFFERS = [
    (
        "umrah-comfort-offer", "عرض العمرة المريحة", "Umrah Comfort Offer",
        "PACKAGE", "3200.00", "2800.00", "1580418827493-f2b22c0a76cb", -7, 45, True,
        "خصم على باقة العمرة لأربعة أيام بإقامة قريبة من الحرم، للحجز المبكر.",
        "A discount on the four-day Umrah package near the Haram, for early bookings.",
    ),
    (
        "alula-weekend-offer", "عرض نهاية الأسبوع في العلا", "AlUla Weekend Offer",
        "PACKAGE", "3900.00", "3400.00", "1547234935-80c7145ec969", -3, 30, True,
        "ثلاثة أيام في العلا شاملة الطيران الداخلي وتذاكر الحِجر.",
        "Three days in AlUla including domestic flights and Hegra tickets.",
    ),
    (
        "dubai-flight-offer", "عرض الطيران إلى دبي", "Dubai Flight Offer",
        "FLIGHT", "1100.00", "890.00", "1512453979798-5ea266f8880c", -10, 25, True,
        "ذهاب وعودة من الرياض إلى دبي، بأمتعة 30 كجم.",
        "Return Riyadh to Dubai, with 30kg of baggage.",
    ),
    (
        "istanbul-hotel-offer", "عرض فنادق إسطنبول", "Istanbul Hotel Offer",
        "HOTEL", "780.00", "620.00", "1541432901042-2d8bd64b4a9b", -14, 40, False,
        "الليلة في فندق أربع نجوم بتقسيم، شاملة الإفطار.",
        "A night in a four-star hotel in Taksim, breakfast included.",
    ),
    (
        "turkiye-visa-offer", "عرض تأشيرة تركيا", "Türkiye Visa Offer",
        "VISA", "450.00", "350.00", "1541432901042-2d8bd64b4a9b", -5, 60, False,
        "رسوم خدمة مخفّضة على التأشيرة السياحية، مع متابعة الطلب حتى الإصدار.",
        "A reduced service fee on the tourist visa, with the application followed through to issue.",
    ),
    (
        "red-sea-cruise-offer", "عرض رحلة البحر الأحمر", "Red Sea Cruise Offer",
        "CRUISE", "6900.00", "6200.00", "1548574505-5e239809ee19", 20, 80, False,
        "سبع ليالٍ تنطلق من جدة — يبدأ الحجز قريبًا.",
        "Seven nights sailing from Jeddah — booking opens soon.",
    ),
]
# fmt: on


class Command(BaseCommand):
    help = "Load the demo offers. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")
        parser.add_argument(
            "--keep-extras",
            action="store_true",
            help="Leave offers that are not in this list alone.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        guard_demo_write(options["force"])
        today = timezone.localdate()

        for row in OFFERS:
            (
                slug,
                title_ar,
                title_en,
                service,
                before,
                after,
                image,
                starts,
                ends,
                featured,
                desc_ar,
                desc_en,
            ) = row
            Offer.objects.update_or_create(
                slug=slug,
                defaults={
                    "title_ar": title_ar,
                    "title_en": title_en,
                    "description_ar": desc_ar,
                    "description_en": desc_en,
                    "service_type": service,
                    "price_before": Decimal(before),
                    "price_after": Decimal(after),
                    "image": photo(image),
                    "starts_at": today + timedelta(days=starts),
                    "ends_at": today + timedelta(days=ends),
                    "is_featured": featured,
                    "is_active": True,
                },
            )

        # The rows that shipped with the scaffold point at cdn.example.com or
        # carry no image at all, which renders as a hole on the offers rail.
        if not options["keep_extras"]:
            stale = Offer.objects.exclude(slug__in=[row[0] for row in OFFERS])
            if stale.exists():
                self.stdout.write(
                    self.style.WARNING(
                        "Removing offers not in this list: "
                        + ", ".join(stale.values_list("slug", flat=True))
                    )
                )
                stale.delete()

        self.stdout.write(self.style.SUCCESS(f"Offers: {len(OFFERS)} written."))

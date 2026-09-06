"""The add-on services shown as tiles under the search.

These are deliberately NOT flights, hotels, packages, visas and cruises: those
five are the search tabs directly above, and repeating them as cards was the
duplication the client's feedback asked us to remove. What is left is the
things a traveller adds to a trip once the trip itself is decided.

`icon` is a key, not an asset — the frontend maps it to its own component, so
adding a service here needs a matching entry in SERVICE_ICONS.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.services.models import Service
from common.utilities import guard_demo_write

# slug, name_ar, name_en, icon key, description_ar, description_en
# fmt: off
# slug, name_ar, name_en, icon, description_ar, description_en, link
#
# The link is where the tile leads. Blank means the contact form, which is the
# honest answer for an add-on an agent arranges by hand; the two that have a
# page of their own point at it.
SERVICES = [
    ("car-rental", "تأجير السيارات", "Car Rental", "car",
     "سيارة في انتظارك عند الوصول، بتأمين وسائق اختياري.",
     "A car waiting when you land, with insurance and an optional driver.", ""),
    ("airport-transfers", "تنقلات المطار", "Airport Transfers", "transfer",
     "استقبال وتوصيل بين المطار والفندق بسائق يعرف الطريق.",
     "Pick-up and drop-off between airport and hotel with a driver who knows the way.", ""),
    ("international-licence", "الرخصة الدولية", "International Licence", "licence",
     "إصدار رخصة القيادة الدولية قبل السفر، دون مراجعة أي جهة.",
     "An international driving permit issued before you travel, with no office to visit.", ""),
    ("travel-insurance", "تأمين السفر", "Travel Insurance", "shield",
     "تغطية طبية وإلغاء الرحلة، ومطلوبة لتأشيرة شنغن.",
     "Medical and cancellation cover — and required for a Schengen visa.", ""),
    ("internet-packages", "باقات الاتصال والإنترنت", "Internet Packages", "sim",
     "شريحة أو باقة إنترنت تعمل من لحظة هبوط الطائرة.",
     "A SIM or data plan that works from the moment you land.", ""),
    ("activities-tours", "حجز الأنشطة والجولات", "Activities & Tours", "ticket",
     "تذاكر ومعالم وجولات محجوزة مسبقًا، بلا طوابير.",
     "Tickets, attractions and guided tours booked ahead, with no queues.", "/packages"),
    ("instant-visa", "تأشيرة فورية", "Instant Visa", "passport",
     "التأشيرات الإلكترونية التي تصدر خلال ساعات لا أيام.",
     "The e-visas that come back in hours rather than days.", "/visas"),
    ("travel-consultation", "استشارة سفر مجانية", "Free Travel Consultation", "headset",
     "تكلّم مع موظف حجوزات قبل أن تدفع أي شيء.",
     "Talk to a booking agent before you pay for anything.", ""),
]
# fmt: on


class Command(BaseCommand):
    help = "Load the add-on services shown as tiles. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")
        parser.add_argument(
            "--keep-extras",
            action="store_true",
            help="Leave services that are not in this list alone.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        guard_demo_write(options["force"])

        for order, row in enumerate(SERVICES):
            slug, name_ar, name_en, icon, desc_ar, desc_en, link = row
            Service.objects.update_or_create(
                slug=slug,
                defaults={
                    "name_ar": name_ar,
                    "name_en": name_en,
                    "icon": icon,
                    "description_ar": desc_ar,
                    "description_en": desc_en,
                    "link": link,
                    "order": order,
                    "is_active": True,
                },
            )

        # The scaffold seeded flights/hotels/packages/visas/cruises here, and
        # twice over ("flights" and "flight-booking"). They are the search tabs
        # now, so as tiles they were the same five things said again.
        if not options["keep_extras"]:
            stale = Service.objects.exclude(slug__in=[row[0] for row in SERVICES])
            if stale.exists():
                self.stdout.write(
                    self.style.WARNING(
                        "Removing services that duplicate the search tabs: "
                        + ", ".join(stale.values_list("slug", flat=True))
                    )
                )
                stale.delete()

        self.stdout.write(self.style.SUCCESS(f"Services: {len(SERVICES)} written."))

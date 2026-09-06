"""Branch addresses and map pins.

⚠ The addresses and coordinates below are PLACEHOLDERS, exactly as the client's
feedback document says they are. They put a real pin in the right city so the
map card can be judged, and they are not the company's actual offices. Replace
every one from the panel before the site goes live.

The phone numbers are real and were already published; only the addresses and
the pins are invented here.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.company.models import Branch
from common.utilities import guard_demo_write

# phone (the natural key), address_ar, address_en, lat, lng, is_main
BRANCHES = [
    (
        "+966115602558",
        "حي العليا، طريق الملك فهد، الرياض",
        "Al Olaya, King Fahd Road, Riyadh",
        "24.693200", "46.685400", True,
    ),
    (
        "+966112266745",
        "حي الملز، شارع صلاح الدين الأيوبي، الرياض",
        "Al Malaz, Salah Al Din Al Ayoubi Street, Riyadh",
        "24.665600", "46.732800", False,
    ),
    (
        "+966112311372",
        "حي النخيل، طريق الأمير تركي الأول، الرياض",
        "Al Nakheel, Prince Turki Al Awwal Road, Riyadh",
        "24.734900", "46.637300", False,
    ),
    (
        "+966112022107",
        "حي السليمانية، شارع الأمير عبدالعزيز بن مساعد، الرياض",
        "Al Sulaimaniyah, Prince Abdulaziz bin Musaid Street, Riyadh",
        "24.707100", "46.702600", False,
    ),
]


class Command(BaseCommand):
    help = "Fill the branches with placeholder addresses and map pins. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        guard_demo_write(options["force"])

        written = missing = 0
        for phone, address_ar, address_en, lat, lng, is_main in BRANCHES:
            # Matched on the phone rather than created: the branches themselves
            # ship in a migration, and this only fills in what they lack.
            updated = Branch.objects.filter(phone=phone).update(
                address_ar=address_ar,
                address_en=address_en,
                latitude=Decimal(lat),
                longitude=Decimal(lng),
                is_main=is_main,
            )
            written += updated
            missing += 0 if updated else 1

        if missing:
            self.stderr.write(
                self.style.WARNING(f"{missing} branch(es) not found by phone number.")
            )
        self.stdout.write(
            self.style.WARNING(
                "Addresses and pins are placeholders — replace them in the panel "
                "before launch."
            )
        )
        self.stdout.write(self.style.SUCCESS(f"Branches: {written} updated."))

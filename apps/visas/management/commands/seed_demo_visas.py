"""Demo visa countries and the types offered for each.

Demonstration content. The countries are real and the requirement lists are the
ordinary ones; the service fees and the processing times here are ours and are
meant to be replaced — an embassy changes both without notice.

Flags come from flagcdn.com by ISO code rather than being uploaded, so adding a
country needs no artwork.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.visas.models import VisaCountry, VisaType
from common.utilities import guard_demo_write

FLAG = "https://flagcdn.com/w160/{}.png"

REQUIREMENTS_AR = {
    "TOURISM": [
        "جواز سفر ساري لمدة 6 أشهر على الأقل",
        "صورتان شخصيتان بخلفية بيضاء",
        "كشف حساب بنكي لآخر 3 أشهر",
        "حجز طيران وفندق",
        "تأمين سفر",
    ],
    "BUSINESS": [
        "جواز سفر ساري لمدة 6 أشهر على الأقل",
        "خطاب دعوة من الشركة المضيفة",
        "خطاب من جهة العمل يوضح المسمى والراتب",
        "السجل التجاري إن كنت صاحب عمل",
        "كشف حساب بنكي لآخر 3 أشهر",
    ],
    "STUDY": [
        "جواز سفر ساري لمدة 6 أشهر على الأقل",
        "قبول من الجامعة أو المعهد",
        "إثبات القدرة المالية",
        "الشهادات الدراسية السابقة",
        "تأمين صحي",
    ],
    "UMRAH": [
        "جواز سفر ساري لمدة 6 أشهر على الأقل",
        "صورة شخصية بخلفية بيضاء",
        "شهادة التطعيمات المطلوبة",
        "حجز مؤكد للسكن والنقل",
    ],
}

REQUIREMENTS_EN = {
    "TOURISM": [
        "Passport valid for at least 6 months",
        "Two passport photos on a white background",
        "Bank statement for the last 3 months",
        "Flight and hotel bookings",
        "Travel insurance",
    ],
    "BUSINESS": [
        "Passport valid for at least 6 months",
        "Invitation letter from the host company",
        "Employer letter stating role and salary",
        "Commercial registration if self-employed",
        "Bank statement for the last 3 months",
    ],
    "STUDY": [
        "Passport valid for at least 6 months",
        "Acceptance from the university or institute",
        "Proof of funds",
        "Previous academic certificates",
        "Health insurance",
    ],
    "UMRAH": [
        "Passport valid for at least 6 months",
        "Passport photo on a white background",
        "Required vaccination certificate",
        "Confirmed accommodation and transport booking",
    ],
}

# name_ar, name_en, iso2, [(name_ar, name_en, purpose, price, days, validity)]
# One record per row. `ruff format` gives every field its own line and turns a
# readable table into column soup; the project lints with `ruff check`.
# fmt: off
COUNTRIES = [
    ("تركيا", "Türkiye", "tr", [
        ("تأشيرة سياحية", "Tourist visa", "TOURISM", "350.00", 5, 180),
        ("تأشيرة عمل", "Business visa", "BUSINESS", "520.00", 7, 180),
    ]),
    ("المملكة المتحدة", "United Kingdom", "gb", [
        ("تأشيرة زيارة", "Visitor visa", "TOURISM", "1450.00", 20, 180),
        ("تأشيرة دراسية", "Student visa", "STUDY", "780.00", 15, 365),
        ("تأشيرة عمل", "Business visa", "BUSINESS", "1450.00", 20, 180),
    ]),
    ("فرنسا", "France", "fr", [
        ("تأشيرة شنغن السياحية", "Schengen tourist visa", "TOURISM", "980.00", 15, 90),
        ("تأشيرة عمل", "Business visa", "BUSINESS", "450.00", 10, 90),
    ]),
    ("الولايات المتحدة", "United States", "us", [
        ("تأشيرة زيارة B1/B2", "B1/B2 visitor visa", "TOURISM", "1900.00", 30, 3650),
        ("تأشيرة دراسية F1", "F1 student visa", "STUDY", "2100.00", 30, 1825),
    ]),
    ("اليابان", "Japan", "jp", [
        ("تأشيرة سياحية", "Tourist visa", "TOURISM", "640.00", 8, 90),
    ]),
    ("ماليزيا", "Malaysia", "my", [
        ("تصريح دخول إلكتروني", "Electronic travel registration", "TOURISM", "180.00", 3, 90),
    ]),
    ("تايلاند", "Thailand", "th", [
        ("تأشيرة سياحية", "Tourist visa", "TOURISM", "290.00", 5, 60),
    ]),
    ("أذربيجان", "Azerbaijan", "az", [
        ("تأشيرة إلكترونية", "E-visa", "TOURISM", "220.00", 3, 90),
    ]),
    ("جورجيا", "Georgia", "ge", [
        ("تأشيرة سياحية", "Tourist visa", "TOURISM", "260.00", 7, 90),
    ]),
    ("الهند", "India", "in", [
        ("تأشيرة إلكترونية سياحية", "Tourist e-visa", "TOURISM", "310.00", 5, 365),
        ("تأشيرة عمل", "Business visa", "BUSINESS", "540.00", 8, 365),
    ]),
    ("إندونيسيا", "Indonesia", "id", [
        ("تأشيرة عند الوصول", "Visa on arrival", "TOURISM", "200.00", 2, 30),
    ]),
    ("البوسنة والهرسك", "Bosnia and Herzegovina", "ba", [
        ("تأشيرة سياحية", "Tourist visa", "TOURISM", "340.00", 10, 90),
    ]),
]
# fmt: on


class Command(BaseCommand):
    help = "Load the demo visa countries and types. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")
        parser.add_argument(
            "--keep-extras",
            action="store_true",
            help="Leave countries and types that are not in this list alone.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        guard_demo_write(options["force"])

        countries = types = 0
        for name_ar, name_en, iso2, visa_types in COUNTRIES:
            country, _ = VisaCountry.objects.update_or_create(
                name_en=name_en,
                defaults={
                    "name_ar": name_ar,
                    "flag_image": FLAG.format(iso2),
                    "is_active": True,
                },
            )
            countries += 1

            for type_ar, type_en, purpose, price, days, validity in visa_types:
                VisaType.objects.update_or_create(
                    country=country,
                    name_en=type_en,
                    defaults={
                        "name_ar": type_ar,
                        "purpose": purpose,
                        "requirements_ar": "\n".join(REQUIREMENTS_AR[purpose]),
                        "requirements_en": "\n".join(REQUIREMENTS_EN[purpose]),
                        "price": Decimal(price),
                        "processing_time_days": days,
                        "validity_days": validity,
                        "is_active": True,
                    },
                )
                types += 1

        # This table is keyed on the country name, not a slug, so an earlier
        # fixture spelling ("Turkey" beside "Türkiye") survives as a second
        # country and the site offers both. Pruning is what makes the result
        # of a run predictable rather than cumulative.
        if not options["keep_extras"]:
            wanted_countries = [row[1] for row in COUNTRIES]
            stale = VisaCountry.objects.exclude(name_en__in=wanted_countries)
            if stale.exists():
                self.stdout.write(
                    self.style.WARNING(
                        "Removing countries not in this list: "
                        + ", ".join(stale.values_list("name_en", flat=True))
                    )
                )
                stale.delete()

            for name_ar, name_en, iso2, visa_types in COUNTRIES:
                VisaType.objects.filter(country__name_en=name_en).exclude(
                    name_en__in=[t[1] for t in visa_types]
                ).delete()

        self.stdout.write(self.style.SUCCESS(f"Visas: {countries} countries, {types} types."))

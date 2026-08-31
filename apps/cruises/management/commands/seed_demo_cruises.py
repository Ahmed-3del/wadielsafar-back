"""Demo cruises and their port-by-port itineraries.

Demonstration content. The ports and the cruise lines are real; the sailings,
the dates and the fares are ours and are meant to be replaced. Departure dates
are generated relative to today so a re-run never advertises a ship that has
already sailed.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.cruises.models import Cruise, CruiseItinerary
from apps.destinations.models import Destination
from common.utilities import guard_demo_write, photo

CRUISES = [
    {
        "slug": "red-sea-discovery",
        "title_ar": "اكتشف البحر الأحمر",
        "title_en": "Red Sea Discovery",
        "line_ar": "أرويا كروز",
        "line_en": "AROYA Cruises",
        "destination": "jeddah",
        "port_ar": "جدة",
        "port_en": "Jeddah",
        "days_out": 45,
        "nights": 7,
        "price": "6200.00",
        "image": "1548574505-5e239809ee19",
        "featured": True,
        "desc_ar": "سبع ليالٍ على البحر الأحمر تنطلق من جدة، بين جزر وشعاب ومحطات على الساحل المصري.",
        "desc_en": "Seven nights on the Red Sea from Jeddah, between islands, reefs and stops on the Egyptian coast.",
        "included_ar": [
            "كابينة بإطلالة بحرية",
            "جميع الوجبات على متن السفينة",
            "برنامج ترفيهي يومي",
            "رسوم الموانئ",
        ],
        "included_en": [
            "Sea-view cabin",
            "All meals on board",
            "Daily entertainment programme",
            "Port fees",
        ],
        "itinerary": [
            (
                "جدة",
                "Jeddah",
                "الإبحار مساءً بعد التسجيل والاستقرار في الكابينة.",
                "Board in the afternoon and sail in the evening.",
            ),
            (
                "ينبع",
                "Yanbu",
                "يوم على الساحل، مع جولة اختيارية إلى البلدة القديمة.",
                "A day on the coast, with an optional tour of the old town.",
            ),
            (
                "في عرض البحر",
                "At sea",
                "يوم كامل على متن السفينة: مسابح ومطاعم وبرنامج مسائي.",
                "A full day on board: pools, restaurants and an evening programme.",
            ),
            (
                "شرم الشيخ",
                "Sharm El Sheikh",
                "غوص وسنوركل في الشعاب المرجانية.",
                "Diving and snorkelling on the reefs.",
            ),
            (
                "العقبة",
                "Aqaba",
                "رحلة برية اختيارية إلى البتراء.",
                "An optional land trip to Petra.",
            ),
            ("في عرض البحر", "At sea", "يوم راحة قبل العودة.", "A rest day before the return leg."),
            (
                "جدة",
                "Jeddah",
                "الوصول صباحًا وإنهاء الإجراءات.",
                "Arrive in the morning and disembark.",
            ),
        ],
    },
    {
        "slug": "arabian-gulf-escape",
        "title_ar": "جولة الخليج العربي",
        "title_en": "Arabian Gulf Escape",
        "line_ar": "إم إس سي",
        "line_en": "MSC Cruises",
        "destination": "dubai",
        "port_ar": "دبي",
        "port_en": "Dubai",
        "days_out": 38,
        "nights": 5,
        "price": "4100.00",
        "image": "1520175480921-4edfa2983e0f",
        "featured": True,
        "desc_ar": "خمس ليالٍ بين موانئ الخليج، تنطلق وتنتهي في دبي — مناسبة لأول تجربة بحرية.",
        "desc_en": "Five nights between Gulf ports, starting and ending in Dubai — a good first cruise.",
        "included_ar": [
            "كابينة داخلية أو بإطلالة",
            "الإفطار والغداء والعشاء",
            "أنشطة للأطفال",
            "رسوم الموانئ",
        ],
        "included_en": [
            "Inside or sea-view cabin",
            "Breakfast, lunch and dinner",
            "Children's activities",
            "Port fees",
        ],
        "itinerary": [
            (
                "دبي",
                "Dubai",
                "الصعود على متن السفينة والإبحار مساءً.",
                "Board and sail in the evening.",
            ),
            (
                "أبوظبي",
                "Abu Dhabi",
                "جولة إلى جامع الشيخ زايد وجزيرة ياس.",
                "A tour to Sheikh Zayed Mosque and Yas Island.",
            ),
            (
                "صير بني ياس",
                "Sir Bani Yas",
                "جزيرة طبيعية بمحمية ورحلات سفاري.",
                "A nature island with a reserve and safari drives.",
            ),
            (
                "الدوحة",
                "Doha",
                "سوق واقف ومتحف الفن الإسلامي.",
                "Souq Waqif and the Museum of Islamic Art.",
            ),
            ("دبي", "Dubai", "العودة صباحًا.", "Return in the morning."),
        ],
    },
    {
        "slug": "mediterranean-classics",
        "title_ar": "كلاسيكيات البحر المتوسط",
        "title_en": "Mediterranean Classics",
        "line_ar": "كوستا",
        "line_en": "Costa Cruises",
        "destination": "istanbul",
        "port_ar": "إسطنبول",
        "port_en": "Istanbul",
        "days_out": 70,
        "nights": 8,
        "price": "7400.00",
        "image": "1520175480921-4edfa2983e0f",
        "featured": False,
        "desc_ar": "ثماني ليالٍ من إسطنبول إلى الجزر اليونانية والساحل التركي.",
        "desc_en": "Eight nights from Istanbul to the Greek islands and the Turkish coast.",
        "included_ar": ["كابينة بشرفة", "جميع الوجبات", "عروض مسائية", "رسوم الموانئ"],
        "included_en": ["Balcony cabin", "All meals", "Evening shows", "Port fees"],
        "itinerary": [
            (
                "إسطنبول",
                "Istanbul",
                "الإبحار عبر البوسفور عند الغروب.",
                "Sail out through the Bosphorus at sunset.",
            ),
            ("إزمير", "İzmir", "زيارة أفسس الأثرية.", "A visit to ancient Ephesus."),
            (
                "ميكونوس",
                "Mykonos",
                "البلدة البيضاء والطواحين.",
                "The white town and the windmills.",
            ),
            (
                "سانتوريني",
                "Santorini",
                "إطلالة الكالديرا وقرية أويا.",
                "The caldera view and the village of Oia.",
            ),
            ("أثينا", "Athens", "الأكروبوليس والمدينة القديمة.", "The Acropolis and the old city."),
            ("في عرض البحر", "At sea", "يوم على متن السفينة.", "A day on board."),
            ("بودروم", "Bodrum", "القلعة والمرسى.", "The castle and the marina."),
            ("إسطنبول", "Istanbul", "الوصول وإنهاء الإجراءات.", "Arrive and disembark."),
        ],
    },
    {
        "slug": "asian-islands-voyage",
        "title_ar": "رحلة الجزر الآسيوية",
        "title_en": "Asian Islands Voyage",
        "line_ar": "رويال كاريبيان",
        "line_en": "Royal Caribbean",
        "destination": "phuket",
        "port_ar": "سنغافورة",
        "port_en": "Singapore",
        "days_out": 85,
        "nights": 6,
        "price": "5800.00",
        "image": "1548574505-5e239809ee19",
        "featured": False,
        "desc_ar": "ست ليالٍ بين سنغافورة وجزر تايلاند وماليزيا، بسفينة مجهّزة للعائلات.",
        "desc_en": "Six nights between Singapore and the islands of Thailand and Malaysia, on a ship built for families.",
        "included_ar": ["كابينة عائلية", "جميع الوجبات", "نادي الأطفال", "رسوم الموانئ"],
        "included_en": ["Family cabin", "All meals", "Kids' club", "Port fees"],
        "itinerary": [
            ("سنغافورة", "Singapore", "الصعود والإبحار.", "Board and sail."),
            ("بينانج", "Penang", "جورج تاون ومطاعم الشارع.", "George Town and the street food."),
            (
                "بوكيت",
                "Phuket",
                "الشواطئ ورحلة إلى جزر في في.",
                "The beaches and a trip to the Phi Phi islands.",
            ),
            (
                "لنكاوي",
                "Langkawi",
                "التلفريك والشواطئ الهادئة.",
                "The cable car and the quiet beaches.",
            ),
            ("في عرض البحر", "At sea", "يوم على متن السفينة.", "A day on board."),
            ("سنغافورة", "Singapore", "العودة صباحًا.", "Return in the morning."),
        ],
    },
    {
        "slug": "aroya-winter-sailing",
        "title_ar": "إبحار أرويا الشتوي",
        "title_en": "AROYA Winter Sailing",
        "line_ar": "أرويا كروز",
        "line_en": "AROYA Cruises",
        "destination": "jeddah",
        "port_ar": "جدة",
        "port_en": "Jeddah",
        "days_out": 100,
        "nights": 4,
        "price": "3600.00",
        "image": "1548574505-5e239809ee19",
        "featured": False,
        "desc_ar": "أربع ليالٍ قصيرة على البحر الأحمر، مناسبة لإجازة نهاية الأسبوع الطويلة.",
        "desc_en": "A short four nights on the Red Sea, built around a long weekend.",
        "included_ar": ["كابينة داخلية", "جميع الوجبات", "برنامج ترفيهي", "رسوم الموانئ"],
        "included_en": ["Inside cabin", "All meals", "Entertainment programme", "Port fees"],
        "itinerary": [
            ("جدة", "Jeddah", "الإبحار مساءً.", "Sail in the evening."),
            ("ينبع", "Yanbu", "يوم على الساحل.", "A day on the coast."),
            ("في عرض البحر", "At sea", "يوم على متن السفينة.", "A day on board."),
            ("جدة", "Jeddah", "الوصول صباحًا.", "Arrive in the morning."),
        ],
    },
]


class Command(BaseCommand):
    help = "Load the demo cruises and their itineraries. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        guard_demo_write(options["force"])
        today = timezone.localdate()

        written = 0
        for spec in CRUISES:
            destination = Destination.objects.filter(slug=spec["destination"]).first()

            cruise, _ = Cruise.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "title_ar": spec["title_ar"],
                    "title_en": spec["title_en"],
                    "cruise_line_ar": spec["line_ar"],
                    "cruise_line_en": spec["line_en"],
                    "destination": destination,
                    "departure_port_ar": spec["port_ar"],
                    "departure_port_en": spec["port_en"],
                    "description_ar": spec["desc_ar"],
                    "description_en": spec["desc_en"],
                    "departure_date": today + timedelta(days=spec["days_out"]),
                    "duration_nights": spec["nights"],
                    "price_from": Decimal(spec["price"]),
                    "currency": "SAR",
                    "cover_image": photo(spec["image"]),
                    "included_services_ar": "\n".join(spec["included_ar"]),
                    "included_services_en": "\n".join(spec["included_en"]),
                    "is_featured": spec["featured"],
                    "is_active": True,
                },
            )

            for day, (port_ar, port_en, desc_ar, desc_en) in enumerate(spec["itinerary"], start=1):
                CruiseItinerary.objects.update_or_create(
                    cruise=cruise,
                    day_number=day,
                    defaults={
                        "port_ar": port_ar,
                        "port_en": port_en,
                        "description_ar": desc_ar,
                        "description_en": desc_en,
                    },
                )
            # A shortened sailing must not leave orphan days from a previous run.
            cruise.itinerary.filter(day_number__gt=len(spec["itinerary"])).delete()
            written += 1

        self.stdout.write(self.style.SUCCESS(f"Cruises: {written} written."))

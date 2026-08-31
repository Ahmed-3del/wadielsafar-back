"""Demo flight deals.

Demonstration content. The airports, airlines and routes are real; the fares
and the dates are ours and are meant to be replaced. Departure dates are
generated relative to today so a re-run never leaves the site advertising a
flight that has already left.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.flights.models import FlightDeal
from common.utilities import guard_demo_write

# slug, origin (code, ar, en), destination (code, ar, en), airline ar/en,
# cabin, price, days from today until departure, nights away, baggage, featured
# One record per row. `ruff format` gives every field its own line and turns a
# readable table into column soup; the project lints with `ruff check`.
# fmt: off
FLIGHTS = [
    ("riyadh-to-dubai", ("RUH", "الرياض", "Riyadh"), ("DXB", "دبي", "Dubai"),
     "طيران السعودية", "Saudia", "ECONOMY", "890.00", 21, 5, 30, True),
    ("riyadh-to-cairo", ("RUH", "الرياض", "Riyadh"), ("CAI", "القاهرة", "Cairo"),
     "مصر للطيران", "EgyptAir", "ECONOMY", "1250.00", 28, 7, 30, True),
    ("jeddah-to-istanbul", ("JED", "جدة", "Jeddah"), ("IST", "إسطنبول", "Istanbul"),
     "الخطوط التركية", "Turkish Airlines", "ECONOMY", "1450.00", 30, 7, 30, True),
    ("riyadh-to-istanbul", ("RUH", "الرياض", "Riyadh"), ("IST", "إسطنبول", "Istanbul"),
     "طيران ناس", "flynas", "ECONOMY", "1320.00", 35, 6, 25, False),
    ("jeddah-to-dubai", ("JED", "جدة", "Jeddah"), ("DXB", "دبي", "Dubai"),
     "طيران الإمارات", "Emirates", "ECONOMY", "980.00", 18, 4, 30, False),
    ("riyadh-to-london", ("RUH", "الرياض", "Riyadh"), ("LHR", "لندن", "London"),
     "الخطوط البريطانية", "British Airways", "ECONOMY", "3450.00", 45, 10, 46, True),
    ("jeddah-to-kuala-lumpur", ("JED", "جدة", "Jeddah"), ("KUL", "كوالالمبور", "Kuala Lumpur"),
     "الخطوط الماليزية", "Malaysia Airlines", "ECONOMY", "2790.00", 50, 9, 30, False),
    ("riyadh-to-tbilisi", ("RUH", "الرياض", "Riyadh"), ("TBS", "تبليسي", "Tbilisi"),
     "طيران ناس", "flynas", "ECONOMY", "1590.00", 33, 6, 25, False),
    ("dammam-to-cairo", ("DMM", "الدمام", "Dammam"), ("CAI", "القاهرة", "Cairo"),
     "طيران أديل", "flyadeal", "ECONOMY", "1150.00", 24, 6, 20, False),
    ("riyadh-to-baku", ("RUH", "الرياض", "Riyadh"), ("GYD", "باكو", "Baku"),
     "الخطوط الأذربيجانية", "Azerbaijan Airlines", "ECONOMY", "1680.00", 40, 5, 30, False),
    ("jeddah-to-paris", ("JED", "جدة", "Jeddah"), ("CDG", "باريس", "Paris"),
     "الخطوط الفرنسية", "Air France", "BUSINESS", "8900.00", 55, 8, 46, False),
    ("riyadh-to-male", ("RUH", "الرياض", "Riyadh"), ("MLE", "ماليه", "Malé"),
     "طيران السعودية", "Saudia", "ECONOMY", "3100.00", 60, 7, 30, True),
]
# fmt: on


class Command(BaseCommand):
    help = "Load the demo flight deals. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        guard_demo_write(options["force"])
        today = timezone.localdate()

        for row in FLIGHTS:
            (
                slug,
                origin,
                dest,
                airline_ar,
                airline_en,
                cabin,
                price,
                days_out,
                nights,
                baggage,
                featured,
            ) = row
            departure = today + timedelta(days=days_out)

            FlightDeal.objects.update_or_create(
                slug=slug,
                defaults={
                    "title_ar": f"{origin[1]} إلى {dest[1]}",
                    "title_en": f"{origin[2]} to {dest[2]}",
                    "origin_city_ar": origin[1],
                    "origin_city_en": origin[2],
                    "origin_airport_code": origin[0],
                    "destination_city_ar": dest[1],
                    "destination_city_en": dest[2],
                    "destination_airport_code": dest[0],
                    "airline_name_ar": airline_ar,
                    "airline_name_en": airline_en,
                    "trip_type": "ROUND_TRIP",
                    "cabin_class": cabin,
                    "price_from": Decimal(price),
                    "currency": "SAR",
                    "departure_date": departure,
                    "return_date": departure + timedelta(days=nights),
                    "baggage_allowance_kg": baggage,
                    "is_featured": featured,
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Flights: {len(FLIGHTS)} written."))

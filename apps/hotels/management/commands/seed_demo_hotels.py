"""Demo hotels, and the amenity list they are tagged with.

Demonstration content. The properties are real hotels, but the nightly rates
here are ours and are meant to be replaced — the site says as much wherever a
price appears.
"""

from datetime import time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.destinations.models import Destination
from apps.hotels.models import Hotel, HotelAmenity
from common.utilities import guard_demo_write, photo

# slug, name_ar, name_en, icon
AMENITIES = [
    ("free-wifi", "واي فاي مجاني", "Free WiFi", "wifi"),
    ("breakfast", "إفطار مشمول", "Breakfast included", "meal"),
    ("pool", "مسبح", "Pool", "pool"),
    ("family-rooms", "غرف عائلية", "Family rooms", "users"),
    ("airport-transfer", "توصيل من المطار", "Airport transfer", "car"),
    ("gym", "نادٍ رياضي", "Gym", "gym"),
    ("spa", "سبا", "Spa", "spa"),
    ("parking", "موقف خاص", "Parking", "car"),
    ("prayer-room", "مصلى", "Prayer room", "prayer"),
    ("beach-access", "إطلالة على البحر", "Beach access", "beach"),
]

# slug, name_ar, name_en, destination slug, stars, price, photo id,
# address_ar, address_en, description_ar, description_en, amenity slugs
# One record per row. `ruff format` gives every field its own line and turns a
# readable table into column soup; the project lints with `ruff check`.
# fmt: off
HOTELS = [
    (
        "burj-al-arab", "برج العرب", "Burj Al Arab", "dubai", 5, "2400.00",
        "1566073771259-6a8506099945",
        "شارع جميرا، دبي", "Jumeirah Street, Dubai",
        "أجنحة على طابقين بإطلالة على الخليج، وخدمة شخصية على مدار الساعة.",
        "Two-storey suites looking over the Gulf, with round-the-clock personal service.",
        ["free-wifi", "breakfast", "pool", "spa", "gym", "beach-access", "prayer-room"],
    ),
    (
        "address-downtown", "العنوان وسط المدينة", "Address Downtown", "dubai", 5, "1450.00",
        "1551882547-ff40c63fe5fa",
        "وسط مدينة دبي", "Downtown Dubai",
        "على بعد دقائق من دبي مول وبرج خليفة، بغرف عائلية تطل على النافورة.",
        "Minutes from Dubai Mall and the Burj Khalifa, with family rooms overlooking the fountain.",
        ["free-wifi", "breakfast", "pool", "family-rooms", "gym", "parking"],
    ),
    (
        "oasis-resort", "منتجع الواحة", "Oasis Resort", "dubai", 4, "1750.50",
        "1571003123894-1f0594d2b5d9",
        "منطقة النخلة، دبي", "Palm area, Dubai",
        "منتجع هادئ بمسبح كبير وشاطئ خاص، مناسب للإقامات الطويلة مع الأطفال.",
        "A quiet resort with a large pool and a private beach, suited to longer stays with children.",
        ["free-wifi", "breakfast", "pool", "family-rooms", "beach-access", "airport-transfer"],
    ),
    (
        "istanbul-park-hotel", "فندق إسطنبول بارك", "Istanbul Park Hotel", "istanbul", 4, "620.00",
        "1590490360182-c33d57733427",
        "تقسيم، إسطنبول", "Taksim, Istanbul",
        "في قلب تقسيم، على مسافة مشي من شارع الاستقلال ومحطة المترو.",
        "In the heart of Taksim, walking distance from İstiklal Street and the metro.",
        ["free-wifi", "breakfast", "family-rooms", "prayer-room", "parking"],
    ),
    (
        "bosphorus-view-hotel", "فندق إطلالة البوسفور", "Bosphorus View Hotel", "istanbul", 5, "980.00",
        "1566073771259-6a8506099945",
        "بشكتاش، إسطنبول", "Beşiktaş, Istanbul",
        "غرف تطل مباشرة على المضيق، وإفطار تركي مفتوح على الشرفة.",
        "Rooms looking straight onto the strait, with an open Turkish breakfast on the terrace.",
        ["free-wifi", "breakfast", "spa", "gym", "airport-transfer"],
    ),
    (
        "makkah-haram-tower", "برج مكة للحرم", "Makkah Haram Tower", "makkah", 5, "1100.00",
        "1580418827493-f2b22c0a76cb",
        "أجياد، مكة المكرمة", "Ajyad, Makkah",
        "على بعد دقائق مشيًا من المسجد الحرام، بغرف عائلية واسعة وخدمة على مدار الساعة.",
        "A few minutes' walk from the Haram, with spacious family rooms and 24-hour service.",
        ["free-wifi", "breakfast", "family-rooms", "prayer-room", "airport-transfer"],
    ),
    (
        "jeddah-corniche-hotel", "فندق كورنيش جدة", "Jeddah Corniche Hotel", "jeddah", 4, "540.00",
        "1520250497591-112f2f40a3f4",
        "الكورنيش، جدة", "The Corniche, Jeddah",
        "على الواجهة البحرية مباشرة، قريب من البلد التاريخية والمطاعم.",
        "Right on the waterfront, close to historic Al-Balad and the restaurants.",
        ["free-wifi", "breakfast", "pool", "beach-access", "parking", "prayer-room"],
    ),
    (
        "alula-desert-lodge", "نزل العلا الصحراوي", "AlUla Desert Lodge", "alula", 4, "890.00",
        "1571003123894-1f0594d2b5d9",
        "وادي عشار، العلا", "Ashar Valley, AlUla",
        "أجنحة بين الجبال الرملية، وجولات مسائية لمشاهدة النجوم.",
        "Suites among the sandstone cliffs, with evening stargazing tours.",
        ["free-wifi", "breakfast", "family-rooms", "airport-transfer", "prayer-room"],
    ),
    (
        "maldives-water-villa", "منتجع فلل المالديف المائية", "Maldives Water Villa Resort",
        "maldives", 5, "3200.00",
        "1520250497591-112f2f40a3f4",
        "أتول مالي الجنوبي", "South Malé Atoll",
        "فلل فوق الماء بمسبح خاص، وانتقال بالطائرة المائية من ماليه.",
        "Overwater villas with private pools, and a seaplane transfer from Malé.",
        ["free-wifi", "breakfast", "pool", "spa", "beach-access", "airport-transfer"],
    ),
    (
        "tbilisi-old-town-hotel", "فندق تبليسي القديمة", "Tbilisi Old Town Hotel", "georgia", 4, "410.00",
        "1590490360182-c33d57733427",
        "البلدة القديمة، تبليسي", "Old Town, Tbilisi",
        "في البلدة القديمة بين الحمامات الكبريتية والمطاعم، بأسعار تناسب العائلات.",
        "In the old town between the sulphur baths and the restaurants, at prices families can plan around.",
        ["free-wifi", "breakfast", "family-rooms", "parking"],
    ),
    (
        "kl-city-centre-hotel", "فندق وسط كوالالمبور", "KL City Centre Hotel", "kuala-lumpur", 4, "480.00",
        "1551882547-ff40c63fe5fa",
        "بوكيت بينتانج، كوالالمبور", "Bukit Bintang, Kuala Lumpur",
        "بجوار البرجين التوأم، ومطاعم حلال في كل اتجاه.",
        "Next to the Twin Towers, with halal restaurants in every direction.",
        ["free-wifi", "breakfast", "pool", "family-rooms", "gym", "prayer-room"],
    ),
    (
        "bali-ubud-retreat", "منتجع أوبود بالي", "Bali Ubud Retreat", "bali", 5, "1250.00",
        "1571003123894-1f0594d2b5d9",
        "أوبود، بالي", "Ubud, Bali",
        "فلل بمسابح خاصة وسط مدرجات الأرز، وبرنامج سبا يومي.",
        "Villas with private pools among the rice terraces, and a daily spa programme.",
        ["free-wifi", "breakfast", "pool", "spa", "airport-transfer"],
    ),
]
# fmt: on


class Command(BaseCommand):
    help = "Load the demo hotels and amenity list. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")
        parser.add_argument(
            "--keep-extras",
            action="store_true",
            help="Leave amenities that are not in this list alone.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        guard_demo_write(options["force"])

        amenities = {}
        for slug, name_ar, name_en, icon in AMENITIES:
            amenities[slug] = HotelAmenity.objects.update_or_create(
                slug=slug,
                defaults={"name_ar": name_ar, "name_en": name_en, "icon": icon},
            )[0]

        # An earlier fixture left "swimming-pool" beside "pool", so hotels
        # could be tagged with both spellings of one amenity.
        if not options["keep_extras"]:
            stale = HotelAmenity.objects.exclude(slug__in=[a[0] for a in AMENITIES])
            if stale.exists():
                self.stdout.write(
                    self.style.WARNING(
                        "Removing amenities not in this list: "
                        + ", ".join(stale.values_list("slug", flat=True))
                    )
                )
                stale.delete()

        written = skipped = 0
        for row in HOTELS:
            (
                slug,
                name_ar,
                name_en,
                dest_slug,
                stars,
                price,
                image,
                addr_ar,
                addr_en,
                desc_ar,
                desc_en,
                amenity_slugs,
            ) = row

            destination = Destination.objects.filter(slug=dest_slug).first()
            if destination is None:
                # Rather than fail the whole run: seed_demo_destinations has
                # simply not been run yet, and saying so is more useful.
                self.stderr.write(
                    self.style.WARNING(f"Skipping {slug}: no destination '{dest_slug}'.")
                )
                skipped += 1
                continue

            hotel, _ = Hotel.objects.update_or_create(
                slug=slug,
                defaults={
                    "name_ar": name_ar,
                    "name_en": name_en,
                    "destination": destination,
                    "star_rating": stars,
                    "address_ar": addr_ar,
                    "address_en": addr_en,
                    "description_ar": desc_ar,
                    "description_en": desc_en,
                    "price_per_night_from": Decimal(price),
                    "currency": "SAR",
                    "cover_image": photo(image),
                    "check_in_time": time(15, 0),
                    "check_out_time": time(12, 0),
                    "is_featured": stars == 5,
                    "is_active": True,
                },
            )
            hotel.amenities.set([amenities[key] for key in amenity_slugs])
            written += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Hotels: {written} written, {skipped} skipped; {len(AMENITIES)} amenities."
            )
        )

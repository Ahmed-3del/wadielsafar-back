"""The destinations the rest of the demo content hangs off.

Hotels, packages and cruises all point at a destination, so this runs first.

This is demonstration content, not the company's own catalogue. Every row is
editable in the panel and is meant to be replaced — the places and countries
are real, the descriptions are ours.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.destinations.models import Destination
from common.utilities import guard_demo_write, photo

# slug, name_ar, name_en, country_ar, country_en, photo id, description_ar, description_en
# One record per row. `ruff format` gives every field its own line and turns a
# readable table into column soup; the project lints with `ruff check`.
# fmt: off
DESTINATIONS = [
    (
        "riyadh", "الرياض", "Riyadh", "السعودية", "Saudi Arabia",
        "1586724237569-f3d0c1dee8c6",
        "العاصمة التي تتغيّر كل موسم: أبراج، ومطاعم، ومواسم ترفيهية، وصحراء تبدأ عند أطراف المدينة.",
        "A capital that changes with every season: towers, restaurants, entertainment seasons, and desert that starts at the city's edge.",
    ),
    (
        "jeddah", "جدة", "Jeddah", "السعودية", "Saudi Arabia",
        "",
        "بوابة الحرمين وعروس البحر الأحمر، بين البلد التاريخية والكورنيش والغوص في الشعاب المرجانية.",
        "The gateway to the Two Holy Mosques and the Red Sea's own city — historic Al-Balad, the corniche, and reef diving.",
    ),
    (
        "makkah", "مكة المكرمة", "Makkah", "السعودية", "Saudi Arabia",
        "1580418827493-f2b22c0a76cb",
        "رحلات العمرة على مدار العام، بإقامة قريبة من الحرم وبرنامج يناسب العائلات وكبار السن.",
        "Umrah trips all year round, with a stay close to the Haram and a programme that suits families and older travellers.",
    ),
    (
        "alula", "العلا", "AlUla", "السعودية", "Saudi Arabia",
        "1547234935-80c7145ec969",
        "مقابر الحِجر النبطية، ومرايا، وجبال من الحجر الرملي — أقرب وجهة عالمية داخل السعودية.",
        "The Nabataean tombs of Hegra, Maraya, and sandstone canyons — Saudi Arabia's own world-class destination.",
    ),
    (
        "dubai", "دبي", "Dubai", "الإمارات", "United Arab Emirates",
        "1512453979798-5ea266f8880c",
        "المدينة التي لا تتوقف: تسوّق، ومطاعم، ومدن ملاهٍ، وصحراء على بعد نصف ساعة من وسط المدينة.",
        "The city that never pauses: shopping, restaurants, theme parks, and desert half an hour from downtown.",
    ),
    (
        "salalah", "صلالة", "Salalah", "عُمان", "Oman",
        "1509233725247-49e657c54213",
        "خريف صلالة: ضباب وشلالات وأودية خضراء بينما تشتد الحرارة في الخليج كله.",
        "The Salalah khareef: mist, waterfalls and green wadis while the rest of the Gulf is at its hottest.",
    ),
    (
        "istanbul", "إسطنبول", "Istanbul", "تركيا", "Türkiye",
        "1541432901042-2d8bd64b4a9b",
        "مدينة على قارتين، بأسواقها ومساجدها ومضيق البوسفور الذي يقسمها ويجمعها.",
        "A city on two continents, with its bazaars, its mosques, and the Bosphorus that both divides and joins it.",
    ),
    (
        "trabzon", "طرابزون", "Trabzon", "تركيا", "Türkiye",
        "1605649487212-47bdab064df7",
        "الشمال التركي الأخضر: بحيرة أوزنجول، ودير سوميلا، ومرتفعات تناسب الرحلات العائلية.",
        "Türkiye's green north: Uzungöl, the Sumela Monastery, and highlands made for family trips.",
    ),
    (
        "cairo", "القاهرة", "Cairo", "مصر", "Egypt",
        "1572252009286-268acec5ca0a",
        "الأهرامات والمتحف المصري الكبير ونهر النيل، في مدينة لا تنام ولا تنتهي زيارتها.",
        "The pyramids, the Grand Egyptian Museum and the Nile, in a city that never sleeps and never finishes.",
    ),
    (
        "sharm-el-sheikh", "شرم الشيخ", "Sharm El Sheikh", "مصر", "Egypt",
        "1544551763-46a013bb70d5",
        "غوص وشعاب مرجانية ومنتجعات على البحر الأحمر، برحلات قصيرة ومباشرة من السعودية.",
        "Diving, coral reefs and Red Sea resorts, a short direct flight from Saudi Arabia.",
    ),
    (
        "sarajevo", "سراييفو", "Sarajevo", "البوسنة والهرسك", "Bosnia and Herzegovina",
        "1541849546-216549ae216d",
        "جبال وأنهار وبلدة عثمانية قديمة، ووجهة صيفية معتدلة الحرارة والأسعار.",
        "Mountains, rivers and an old Ottoman quarter — a summer destination that is mild in both climate and cost.",
    ),
    (
        "baku", "باكو", "Baku", "أذربيجان", "Azerbaijan",
        "",
        "المدينة القديمة وأبراج اللهب على بحر قزوين، ورحلة قصيرة لمن يريد أوروبا بميزانية أقل.",
        "The old city and the Flame Towers on the Caspian — a short trip for anyone who wants Europe on a smaller budget.",
    ),
    (
        "georgia", "جورجيا", "Georgia", "جورجيا", "Georgia",
        "",
        "تبليسي وباتومي وجبال القوقاز، بطبيعة خضراء وأسعار في متناول العائلات.",
        "Tbilisi, Batumi and the Caucasus mountains — green country at prices families can plan around.",
    ),
    (
        "london", "لندن", "London", "المملكة المتحدة", "United Kingdom",
        "1513635269975-59663e0ac1ad",
        "المتاحف والمسارح والحدائق، ووجهة تسوّق وعلاج ودراسة في الوقت نفسه.",
        "Museums, theatres and parks — and a destination for shopping, treatment and study at the same time.",
    ),
    (
        "paris", "باريس", "Paris", "فرنسا", "France",
        "1502602898657-3e91760cbb34",
        "برج إيفل واللوفر ونهر السين، مع رحلات يومية إلى ديزني لاند للعائلات.",
        "The Eiffel Tower, the Louvre and the Seine, with day trips to Disneyland for families.",
    ),
    (
        "kuala-lumpur", "كوالالمبور", "Kuala Lumpur", "ماليزيا", "Malaysia",
        "1596422846543-75c6fc197f07",
        "البرجان التوأم والمرتفعات والمطاعم الحلال — الوجهة الآسيوية الأسهل للعائلات السعودية.",
        "The Twin Towers, the highlands and halal dining — the easiest Asian destination for Saudi families.",
    ),
    (
        "bali", "بالي", "Bali", "إندونيسيا", "Indonesia",
        "1537996194471-e657df975ab4",
        "شواطئ ومدرجات أرز ومنتجعات هادئة، وجهة مفضّلة لشهر العسل.",
        "Beaches, rice terraces and quiet resorts — a honeymoon favourite.",
    ),
    (
        "phuket", "بوكيت", "Phuket", "تايلاند", "Thailand",
        "1552465011-b4e21bf6e79a",
        "جزر وشواطئ ورحلات بحرية يومية، بخيارات إقامة تناسب كل ميزانية.",
        "Islands, beaches and daily boat trips, with somewhere to stay at every budget.",
    ),
    (
        "maldives", "جزر المالديف", "Maldives", "المالديف", "Maldives",
        "1514282401047-d79a71a590e8",
        "منتجعات الفلل المائية والمياه الصافية — الوجهة التي تُحجز مرة في العمر.",
        "Overwater villas and clear water — the trip people book once in a lifetime.",
    ),
]
# fmt: on


class Command(BaseCommand):
    help = "Load the demo destinations. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run even when DEBUG is off. This overwrites content, so be sure.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        guard_demo_write(options["force"])

        for order, row in enumerate(DESTINATIONS):
            slug, name_ar, name_en, country_ar, country_en, image, desc_ar, desc_en = row
            Destination.objects.update_or_create(
                slug=slug,
                defaults={
                    "name_ar": name_ar,
                    "name_en": name_en,
                    "country_ar": country_ar,
                    "country_en": country_en,
                    "description_ar": desc_ar,
                    "description_en": desc_en,
                    "cover_image": photo(image),
                    "order": order,
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Destinations: {len(DESTINATIONS)} written."))

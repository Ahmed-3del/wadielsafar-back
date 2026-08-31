"""Fill the demo packages with the content an editor would actually enter.

The package detail page renders a description, an included-services checklist
and a day-by-day programme. Seed rows had none of those, so the page looked
broken when it was only empty — which makes it impossible to judge the design
or to show the client what their own content will look like.

This is demonstration content, not the client's programmes. Everything it
writes is editable in the admin panel and is meant to be replaced.
"""

from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.destinations.models import Destination
from apps.packages.models import Package, PackageCategory, PackageItinerary

CATEGORIES = {
    "family": ("عائلية", "Family"),
    "honeymoon": ("شهر عسل", "Honeymoon"),
    "cultural": ("ثقافية", "Cultural"),
    "adventure": ("مغامرات", "Adventure"),
}

UNSPLASH = "https://images.unsplash.com/photo-{}?w=1600&q=80"
DUBAI_IMAGE = UNSPLASH.format("1512453979798-5ea266f8880c")
ISTANBUL_IMAGE = UNSPLASH.format("1541432901042-2d8bd64b4a9b")
GEORGIA_IMAGE = UNSPLASH.format("1565008447742-97f6f38c985c")
MALDIVES_IMAGE = UNSPLASH.format("1514282401047-d79a71a590e8")

ALULA_IMAGE = UNSPLASH.format("1591604466107-ec97de577aff")
CAIRO_IMAGE = UNSPLASH.format("1572252009286-268acec5ca0a")
MAKKAH_IMAGE = UNSPLASH.format("1591604129939-f1efa4d9f7fa")
KL_IMAGE = UNSPLASH.format("1596422846543-75c6fc197f07")
BAKU_IMAGE = UNSPLASH.format("1596394516093-501ba68a0ba6")
SALALAH_IMAGE = UNSPLASH.format("1547234935-80c7145ec969")
PACKAGES = [
    {
        "slug": "dubai-family-package",
        "title_ar": "باقة دبي العائلية",
        "title_en": "Dubai Family Package",
        "destination": "dubai",
        "category": "family",
        "duration_days": 5,
        "price_from": Decimal("6200.00"),
        "cover_image": DUBAI_IMAGE,
        "is_featured": True,
        "description_ar": (
            "خمسة أيام في دبي مصمّمة للعائلات: إقامة قريبة من المعالم، وبرنامج "
            "يوازن بين المدينة الحديثة والصحراء، ووقت حر كافٍ للتسوق والراحة.\n\n"
            "يشمل البرنامج الاستقبال من المطار والتنقلات بين الأنشطة، ويمكن تبديل "
            "الجولات أو إضافة ليالٍ بحسب ما يناسبكم."
        ),
        "description_en": (
            "Five days in Dubai built around families: a stay close to the landmarks, "
            "a programme that balances the modern city with the desert, and enough free "
            "time for shopping and rest.\n\n"
            "Airport pick-up and transfers between activities are included, and tours can "
            "be swapped or nights added to suit you."
        ),
        "included_ar": [
            "تذاكر طيران ذهاب وعودة من الرياض أو جدة",
            "إقامة 4 ليالٍ في فندق 4 نجوم مع الإفطار",
            "الاستقبال والتوديع من مطار دبي",
            "تنقلات خاصة بين الفندق والجولات",
            "تذاكر برج خليفة — الطابقان 124 و125",
            "رحلة سفاري صحراوية مع العشاء",
            "زيارة دبي مول وعرض نافورة دبي",
            "تأشيرة دخول الإمارات",
            "مرافقة ناطقة بالعربية طوال البرنامج",
        ],
        "included_en": [
            "Return flights from Riyadh or Jeddah",
            "Four nights in a four-star hotel with breakfast",
            "Airport pick-up and drop-off in Dubai",
            "Private transfers between the hotel and activities",
            "Burj Khalifa tickets — levels 124 and 125",
            "Desert safari with dinner",
            "Dubai Mall and the Dubai Fountain show",
            "UAE entry visa",
            "An Arabic-speaking guide throughout",
        ],
        "itinerary": [
            (
                "الوصول والاستقبال",
                "Arrival and check-in",
                "استقبال في مطار دبي والانتقال إلى الفندق. بقية اليوم حرة للراحة أو "
                "نزهة قصيرة على الواجهة البحرية.",
                "Met at Dubai airport and transferred to the hotel. The rest of the day is "
                "free to rest or take a short walk along the waterfront.",
            ),
            (
                "برج خليفة ودبي مول",
                "Burj Khalifa and Dubai Mall",
                "زيارة برج خليفة والصعود إلى الطابق 124، ثم وقت حر في دبي مول ينتهي "
                "بعرض نافورة دبي مساءً.",
                "Burj Khalifa with access to level 124, then free time in Dubai Mall, ending "
                "with the Dubai Fountain show in the evening.",
            ),
            (
                "سفاري الصحراء",
                "Desert safari",
                "صباح حر، وبعد الظهر رحلة بالسيارات الرباعية إلى الصحراء مع ركوب الجمال "
                "والعشاء في المخيم.",
                "A free morning, then an afternoon dune drive into the desert with camel "
                "rides and dinner at the camp.",
            ),
            (
                "دبي القديمة والخور",
                "Old Dubai and the Creek",
                "جولة في حي الفهيدي وسوق الذهب وسوق التوابل، مع عبور الخور بقارب العبرة.",
                "A walk through Al Fahidi, the Gold Souk and the Spice Souk, crossing the "
                "Creek by abra.",
            ),
            (
                "وقت حر والمغادرة",
                "Free time and departure",
                "وقت حر حتى موعد تسجيل المغادرة، ثم التوصيل إلى المطار.",
                "Free time until check-out, then a transfer to the airport.",
            ),
        ],
    },
    {
        "slug": "dubai-family-holiday",
        "title_ar": "عطلة العائلة في دبي",
        "title_en": "Dubai Family Holiday",
        "destination": "dubai",
        "category": "family",
        "duration_days": 4,
        "price_from": Decimal("3900.00"),
        "cover_image": DUBAI_IMAGE,
        "is_featured": True,
        "description_ar": (
            "أربعة أيام في دبي للعائلات المسافرة مع أطفال: مدن ألعاب مائية، وأنشطة "
            "داخلية مكيّفة تناسب الصيف، وإقامة على مسافة قريبة من المترو."
        ),
        "description_en": (
            "Four days in Dubai for families travelling with children: water parks, "
            "air-conditioned indoor attractions that work in summer, and a stay within "
            "easy reach of the metro."
        ),
        "included_ar": [
            "تذاكر طيران ذهاب وعودة",
            "إقامة 3 ليالٍ في فندق 4 نجوم مع الإفطار",
            "الاستقبال والتوديع من المطار",
            "تذاكر أكوافنتشر ووتربارك",
            "تذاكر أكواريوم دبي وحديقة الحيوانات المائية",
            "تنقلات بين الفندق والأنشطة",
            "تأشيرة دخول الإمارات",
        ],
        "included_en": [
            "Return flights",
            "Three nights in a four-star hotel with breakfast",
            "Airport pick-up and drop-off",
            "Aquaventure Waterpark tickets",
            "Dubai Aquarium and Underwater Zoo tickets",
            "Transfers between the hotel and activities",
            "UAE entry visa",
        ],
        "itinerary": [
            (
                "الوصول",
                "Arrival",
                "استقبال في المطار والانتقال إلى الفندق، ثم وقت حر لبقية اليوم.",
                "Met at the airport and transferred to the hotel, with the rest of the day free.",
            ),
            (
                "أكوافنتشر ووتربارك",
                "Aquaventure Waterpark",
                "يوم كامل في المدينة المائية مع دخول شاطئ المنتجع.",
                "A full day at the water park, including access to the resort beach.",
            ),
            (
                "دبي مول والأكواريوم",
                "Dubai Mall and the Aquarium",
                "زيارة أكواريوم دبي وحديقة الحيوانات المائية، ثم وقت حر للتسوق وعرض النافورة.",
                "Dubai Aquarium and Underwater Zoo, then free time for shopping and the "
                "fountain show.",
            ),
            (
                "وقت حر والمغادرة",
                "Free morning and departure",
                "صباح حر حتى تسجيل المغادرة، ثم التوصيل إلى المطار.",
                "A free morning until check-out, then a transfer to the airport.",
            ),
        ],
    },
    {
        "slug": "classic-istanbul-tour",
        "title_ar": "جولة إسطنبول الكلاسيكية",
        "title_en": "Classic Istanbul Tour",
        "destination": "istanbul",
        "category": "cultural",
        "duration_days": 5,
        "price_from": Decimal("4799.00"),
        "cover_image": ISTANBUL_IMAGE,
        "is_featured": True,
        "description_ar": (
            "خمسة أيام بين ضفتي البوسفور: المعالم العثمانية والبيزنطية أولاً، ثم "
            "الأسواق والمقاهي، مع رحلة بحرية تفصل بين الجانب الأوروبي والآسيوي.\n\n"
            "الجولات بمرشد ناطق بالعربية، والتنقلات بسيارة خاصة."
        ),
        "description_en": (
            "Five days on both sides of the Bosphorus: the Ottoman and Byzantine landmarks "
            "first, then the markets and cafés, with a cruise separating the European and "
            "Asian sides.\n\n"
            "Tours run with an Arabic-speaking guide and transfers are by private car."
        ),
        "included_ar": [
            "تذاكر طيران ذهاب وعودة",
            "إقامة 4 ليالٍ في فندق 4 نجوم بمنطقة السلطان أحمد أو تقسيم",
            "الإفطار يومياً",
            "الاستقبال والتوديع من مطار إسطنبول",
            "جولة المدينة القديمة مع مرشد ناطق بالعربية",
            "رحلة بحرية في مضيق البوسفور",
            "تذاكر دخول المعالم المدرجة في البرنامج",
            "تنقلات داخلية بسيارة خاصة",
        ],
        "included_en": [
            "Return flights",
            "Four nights in a four-star hotel in Sultanahmet or Taksim",
            "Daily breakfast",
            "Airport pick-up and drop-off in Istanbul",
            "Old City tour with an Arabic-speaking guide",
            "Bosphorus cruise",
            "Entry tickets to the sites listed in the programme",
            "Private transfers",
        ],
        "itinerary": [
            (
                "الوصول وتقسيم",
                "Arrival and Taksim",
                "استقبال في المطار والانتقال إلى الفندق، ثم نزهة مسائية في شارع الاستقلال.",
                "Met at the airport and transferred to the hotel, then an evening walk along "
                "İstiklal Street.",
            ),
            (
                "المدينة القديمة",
                "The Old City",
                "آيا صوفيا والمسجد الأزرق وقصر توبكابي وميدان السلطان أحمد مع المرشد.",
                "Hagia Sophia, the Blue Mosque, Topkapı Palace and Sultanahmet Square with "
                "the guide.",
            ),
            (
                "البوسفور والجانب الآسيوي",
                "The Bosphorus and the Asian side",
                "رحلة بحرية في المضيق، ثم جولة في كاديكوي وأسواقها.",
                "A cruise along the strait, then time in Kadıköy and its markets.",
            ),
            (
                "الأسواق ووقت حر",
                "Markets and free time",
                "البازار الكبير وسوق التوابل صباحاً، وبقية اليوم حرة للتسوق أو زيارة برج غلطة.",
                "The Grand Bazaar and Spice Bazaar in the morning, with the rest of the day "
                "free for shopping or Galata Tower.",
            ),
            (
                "المغادرة",
                "Departure",
                "وقت حر حتى تسجيل المغادرة، ثم التوصيل إلى المطار.",
                "Free time until check-out, then a transfer to the airport.",
            ),
        ],
    },
    {
        "slug": "georgia-nature-adventure",
        "title_ar": "مغامرة جورجيا الطبيعية",
        "title_en": "Georgia Nature Adventure",
        "destination": "georgia",
        "category": "adventure",
        "duration_days": 6,
        "price_from": Decimal("5450.00"),
        "cover_image": GEORGIA_IMAGE,
        "is_featured": True,
        "description_ar": (
            "ستة أيام بين تبليسي وجبال القوقاز: مدينة قديمة على ضفاف نهر، وطرق جبلية "
            "تصعد إلى كازبيجي، وتوقفات في قرى النبيذ بإقليم كاخيتي.\n\n"
            "سيارة خاصة مع سائق طوال البرنامج، فالمسافات بين المواقع طويلة."
        ),
        "description_en": (
            "Six days between Tbilisi and the Caucasus: an old city on a riverbank, mountain "
            "roads climbing to Kazbegi, and stops in the wine villages of Kakheti.\n\n"
            "A private car and driver run throughout, because the distances between sites "
            "are long."
        ),
        "included_ar": [
            "تذاكر طيران ذهاب وعودة",
            "إقامة 5 ليالٍ في فنادق 4 نجوم مع الإفطار",
            "الاستقبال والتوديع من مطار تبليسي",
            "سيارة خاصة مع سائق طوال البرنامج",
            "رحلة يوم كامل إلى كازبيجي",
            "جولة كاخيتي مع زيارة مصنع نبيذ",
            "مرشد ناطق بالعربية في الجولات",
        ],
        "included_en": [
            "Return flights",
            "Five nights in four-star hotels with breakfast",
            "Airport pick-up and drop-off in Tbilisi",
            "A private car and driver throughout",
            "A full-day trip to Kazbegi",
            "A Kakheti tour with a winery visit",
            "An Arabic-speaking guide on tours",
        ],
        "itinerary": [
            (
                "الوصول إلى تبليسي",
                "Arrival in Tbilisi",
                "استقبال في المطار والانتقال إلى الفندق، وبقية اليوم حرة.",
                "Met at the airport and transferred to the hotel, with the rest of the day free.",
            ),
            (
                "تبليسي القديمة",
                "Old Tbilisi",
                "جولة سيراً في المدينة القديمة: الحمامات الكبريتية وقلعة ناريكالا وجسر السلام.",
                "A walking tour of the old city: the sulphur baths, Narikala fortress and the "
                "Bridge of Peace.",
            ),
            (
                "متسختا وجفاري",
                "Mtskheta and Jvari",
                "زيارة العاصمة القديمة متسختا ودير جفاري المطل على ملتقى النهرين.",
                "The old capital of Mtskheta and Jvari monastery, overlooking the meeting of "
                "the two rivers.",
            ),
            (
                "كازبيجي",
                "Kazbegi",
                "رحلة يوم كامل على الطريق العسكري الجورجي إلى ستيبانتسميندا وكنيسة جيرجيتي.",
                "A full day along the Georgian Military Highway to Stepantsminda and Gergeti "
                "Trinity Church.",
            ),
            (
                "كاخيتي",
                "Kakheti",
                "بلدة سيغناغي المطلة على الوادي، وزيارة مصنع نبيذ محلي.",
                "The hilltop town of Sighnaghi overlooking the valley, and a local winery visit.",
            ),
            (
                "وقت حر والمغادرة",
                "Free time and departure",
                "وقت حر للتسوق في تبليسي، ثم التوصيل إلى المطار.",
                "Free time for shopping in Tbilisi, then a transfer to the airport.",
            ),
        ],
    },
    {
        "slug": "maldives-honeymoon-escape",
        "title_ar": "رحلة شهر العسل في المالديف",
        "title_en": "Maldives Honeymoon Escape",
        "destination": "maldives",
        "category": "honeymoon",
        "duration_days": 7,
        "price_from": Decimal("12500.00"),
        "cover_image": MALDIVES_IMAGE,
        "is_featured": True,
        "description_ar": (
            "سبعة أيام في جزيرة خاصة: فيلا فوق الماء، وعشاء على الشاطئ، وبرنامج خفيف "
            "يترك معظم الوقت لكما.\n\n"
            "الانتقال من ماليه إلى المنتجع بالطائرة المائية، وهو جزء من الرحلة لا مجرد وسيلة."
        ),
        "description_en": (
            "Seven days on a private island: an overwater villa, dinner on the beach, and a "
            "light programme that leaves most of the time to you.\n\n"
            "The transfer from Malé to the resort is by seaplane — part of the trip rather "
            "than just a way to get there."
        ),
        "included_ar": [
            "تذاكر طيران ذهاب وعودة إلى ماليه",
            "الانتقال من المطار إلى المنتجع بالطائرة المائية",
            "إقامة 6 ليالٍ في فيلا فوق الماء",
            "إفطار وعشاء يومياً",
            "عشاء خاص على الشاطئ مرة واحدة",
            "جلسة تصوير قصيرة عند الغروب",
            "رحلة غطس سطحي بالقارب",
            "ترتيبات شهر العسل في الغرفة",
        ],
        "included_en": [
            "Return flights to Malé",
            "Seaplane transfer from the airport to the resort",
            "Six nights in an overwater villa",
            "Daily breakfast and dinner",
            "One private dinner on the beach",
            "A short sunset photo session",
            "A snorkelling trip by boat",
            "Honeymoon room arrangements",
        ],
        "itinerary": [
            (
                "الوصول والطائرة المائية",
                "Arrival and seaplane",
                "الوصول إلى ماليه والانتقال بالطائرة المائية إلى المنتجع، ثم استلام الفيلا.",
                "Arrive in Malé and transfer by seaplane to the resort, then check in to the villa.",
            ),
            (
                "يوم حر في المنتجع",
                "A free day at the resort",
                "يوم بلا برنامج: الشاطئ أو المسبح أو المنتجع الصحي.",
                "A day with nothing scheduled: the beach, the pool, or the spa.",
            ),
            (
                "غطس سطحي",
                "Snorkelling trip",
                "رحلة بالقارب إلى الشعاب المرجانية القريبة مع المعدات والمرافق.",
                "A boat trip to the nearby reefs, with equipment and a guide.",
            ),
            (
                "عشاء على الشاطئ",
                "Dinner on the beach",
                "يوم حر ينتهي بعشاء خاص على الرمال عند الغروب.",
                "A free day ending with a private dinner on the sand at sunset.",
            ),
            (
                "يوم حر",
                "Free day",
                "وقت مفتوح للراحة أو لأنشطة المنتجع المائية.",
                "Open time to rest or use the resort's water sports.",
            ),
            (
                "الغروب والتصوير",
                "Sunset and photos",
                "جلسة تصوير قصيرة عند الغروب، وبقية اليوم حرة.",
                "A short photo session at sunset, with the rest of the day free.",
            ),
            (
                "المغادرة",
                "Departure",
                "الانتقال بالطائرة المائية إلى ماليه، ثم رحلة العودة.",
                "Seaplane back to Malé, then the return flight.",
            ),
        ],
    },
    {
        "slug": "alula-heritage-weekend",
        "title_ar": "نهاية أسبوع في العلا",
        "title_en": "AlUla Heritage Weekend",
        "destination": "alula",
        "category": "cultural",
        "duration_days": 3,
        "price_from": Decimal("3400.00"),
        "cover_image": ALULA_IMAGE,
        "is_featured": True,
        "description_ar": (
            "ثلاثة أيام بين مقابر الحِجر النبطية والبلدة القديمة وجبل الفيل، "
            "بإقامة في وادي عشار وجولة مسائية لمشاهدة النجوم.\n\n"
            "برنامج قصير يناسب إجازة نهاية الأسبوع، ويمكن تمديده بليلة إضافية."
        ),
        "description_en": (
            "Three days between the Nabataean tombs of Hegra, the old town and Elephant "
            "Rock, staying in Ashar Valley with an evening stargazing tour.\n\n"
            "A short programme built for a long weekend, extendable by a night."
        ),
        "included_ar": [
            "طيران داخلي ذهاب وعودة",
            "إقامة ليلتين مع الإفطار",
            "تذاكر الحِجر والبلدة القديمة",
            "التنقلات الداخلية مع سائق",
        ],
        "included_en": [
            "Return domestic flights",
            "Two nights with breakfast",
            "Hegra and old town tickets",
            "Local transfers with a driver",
        ],
        "itinerary": [
            (
                "الوصول والبلدة القديمة",
                "Arrival and the old town",
                "الوصول ظهرًا والاستقرار، ثم جولة مسائية في بلدة العلا القديمة.",
                "Arrive at midday and settle in, then an evening walk through AlUla old town.",
            ),
            (
                "الحِجر وجبل الفيل",
                "Hegra and Elephant Rock",
                "جولة صباحية في مقابر الحِجر، ووقت حر عند جبل الفيل عند الغروب.",
                "A morning tour of the Hegra tombs, and free time at Elephant Rock at sunset.",
            ),
            (
                "مرايا والعودة",
                "Maraya and departure",
                "زيارة مبنى مرايا ثم التوجه إلى المطار.",
                "Visit the Maraya building, then transfer to the airport.",
            ),
        ],
    },
    {
        "slug": "umrah-comfort-package",
        "title_ar": "باقة العمرة المريحة",
        "title_en": "Umrah Comfort Package",
        "destination": "makkah",
        "category": "cultural",
        "duration_days": 4,
        "price_from": Decimal("2800.00"),
        "cover_image": MAKKAH_IMAGE,
        "is_featured": True,
        "description_ar": (
            "أربعة أيام بإقامة قريبة من المسجد الحرام، ونقل من المطار وإليه، "
            "وبرنامج يناسب العائلات وكبار السن.\n\n"
            "يمكن إضافة ليالٍ في المدينة المنورة ضمن البرنامج نفسه."
        ),
        "description_en": (
            "Four days in a hotel close to the Haram, with airport transfers both ways "
            "and a programme that suits families and older travellers.\n\n"
            "Nights in Madinah can be added to the same booking."
        ),
        "included_ar": [
            "إقامة 3 ليالٍ قرب الحرم مع الإفطار",
            "الاستقبال والتوصيل من المطار",
            "التنقلات بين مكة والمدينة عند الطلب",
            "مرافقة ميدانية طوال البرنامج",
        ],
        "included_en": [
            "Three nights near the Haram with breakfast",
            "Airport pick-up and drop-off",
            "Makkah–Madinah transfers on request",
            "On-the-ground support throughout",
        ],
        "itinerary": [
            (
                "الوصول والاستقبال",
                "Arrival",
                "الاستقبال في المطار والتوجه إلى الفندق، ثم أداء العمرة.",
                "Airport welcome and transfer to the hotel, then performing Umrah.",
            ),
            (
                "يوم في الحرم",
                "A day at the Haram",
                "يوم مفتوح للصلاة والعبادة مع الإفطار في الفندق.",
                "An open day for prayer and worship, with breakfast at the hotel.",
            ),
            (
                "زيارة المعالم",
                "Landmarks",
                "جولة اختيارية إلى المعالم التاريخية حول مكة.",
                "An optional tour of the historic sites around Makkah.",
            ),
            (
                "المغادرة",
                "Departure",
                "طواف الوداع ثم التوصيل إلى المطار.",
                "The farewell tawaf, then a transfer to the airport.",
            ),
        ],
    },
    {
        "slug": "cairo-nile-discovery",
        "title_ar": "القاهرة والنيل",
        "title_en": "Cairo and the Nile",
        "destination": "cairo",
        "category": "cultural",
        "duration_days": 5,
        "price_from": Decimal("4300.00"),
        "cover_image": CAIRO_IMAGE,
        "is_featured": False,
        "description_ar": (
            "خمسة أيام بين الأهرامات والمتحف المصري الكبير وخان الخليلي، "
            "مع عشاء على مركب نيلي.\n\n"
            "يمكن إضافة رحلة داخلية إلى الأقصر وأسوان."
        ),
        "description_en": (
            "Five days between the pyramids, the Grand Egyptian Museum and Khan el-Khalili, "
            "with dinner on a Nile boat.\n\n"
            "A domestic add-on to Luxor and Aswan can be arranged."
        ),
        "included_ar": [
            "طيران ذهاب وعودة",
            "إقامة 4 ليالٍ مع الإفطار",
            "تذاكر الأهرامات والمتحف",
            "مرشد ناطق بالعربية",
        ],
        "included_en": [
            "Return flights",
            "Four nights with breakfast",
            "Pyramids and museum tickets",
            "Arabic-speaking guide",
        ],
        "itinerary": [
            (
                "الوصول",
                "Arrival",
                "الاستقبال من المطار والاستقرار في الفندق.",
                "Airport welcome and check-in.",
            ),
            (
                "الأهرامات وأبو الهول",
                "The pyramids and the Sphinx",
                "يوم كامل في الجيزة مع مرشد.",
                "A full day at Giza with a guide.",
            ),
            (
                "المتحف المصري الكبير",
                "The Grand Egyptian Museum",
                "جولة صباحية في المتحف، ووقت حر بعد الظهر.",
                "A morning at the museum, with free time in the afternoon.",
            ),
            (
                "خان الخليلي والنيل",
                "Khan el-Khalili and the Nile",
                "تسوّق في خان الخليلي وعشاء على مركب نيلي.",
                "Shopping in Khan el-Khalili and dinner on a Nile boat.",
            ),
            (
                "المغادرة",
                "Departure",
                "وقت حر ثم التوصيل إلى المطار.",
                "Free time, then a transfer to the airport.",
            ),
        ],
    },
    {
        "slug": "kuala-lumpur-family-trip",
        "title_ar": "كوالالمبور العائلية",
        "title_en": "Kuala Lumpur Family Trip",
        "destination": "kuala-lumpur",
        "category": "family",
        "duration_days": 6,
        "price_from": Decimal("7200.00"),
        "cover_image": KL_IMAGE,
        "is_featured": False,
        "description_ar": (
            "ستة أيام بين المدينة والمرتفعات، بمطاعم حلال في كل مكان "
            "وبرنامج يناسب الأطفال.\n\n"
            "يمكن إضافة ليالٍ في لنكاوي أو بينانج."
        ),
        "description_en": (
            "Six days between the city and the highlands, with halal food everywhere and "
            "a programme that works for children.\n\n"
            "Nights in Langkawi or Penang can be added."
        ),
        "included_ar": [
            "طيران ذهاب وعودة",
            "إقامة 5 ليالٍ مع الإفطار",
            "جولة المدينة والبرجين التوأم",
            "رحلة يوم كامل إلى مرتفعات جنتنج",
        ],
        "included_en": [
            "Return flights",
            "Five nights with breakfast",
            "City tour and the Twin Towers",
            "A full-day trip to Genting Highlands",
        ],
        "itinerary": [
            ("الوصول", "Arrival", "الاستقبال والاستقرار في الفندق.", "Welcome and check-in."),
            (
                "جولة المدينة",
                "City tour",
                "البرجان التوأم وكهوف باتو والمسجد الوطني.",
                "The Twin Towers, Batu Caves and the National Mosque.",
            ),
            (
                "مرتفعات جنتنج",
                "Genting Highlands",
                "التلفريك ومدينة الملاهي.",
                "The cable car and the theme park.",
            ),
            (
                "يوم حر",
                "Free day",
                "تسوّق في بوكيت بينتانج أو زيارة حديقة الطيور.",
                "Shopping in Bukit Bintang or a visit to the bird park.",
            ),
            (
                "بوتراجايا",
                "Putrajaya",
                "جولة نصف يوم في المدينة الإدارية.",
                "A half-day tour of the administrative city.",
            ),
            (
                "المغادرة",
                "Departure",
                "وقت حر ثم التوصيل إلى المطار.",
                "Free time, then a transfer to the airport.",
            ),
        ],
    },
    {
        "slug": "salalah-khareef-escape",
        "title_ar": "خريف صلالة",
        "title_en": "Salalah Khareef Escape",
        "destination": "salalah",
        "category": "adventure",
        "duration_days": 4,
        "price_from": Decimal("3900.00"),
        "cover_image": SALALAH_IMAGE,
        "is_featured": False,
        "description_ar": (
            "أربعة أيام في موسم الخريف: ضباب وشلالات وأودية خضراء، "
            "وشواطئ هادئة على بحر العرب.\n\n"
            "الموسم قصير — من يونيو إلى سبتمبر — ويُحجز مبكرًا."
        ),
        "description_en": (
            "Four days in the khareef season: mist, waterfalls and green wadis, with quiet "
            "beaches on the Arabian Sea.\n\n"
            "The season is short — June to September — and books up early."
        ),
        "included_ar": [
            "طيران ذهاب وعودة",
            "إقامة 3 ليالٍ مع الإفطار",
            "جولة الأودية والشلالات",
            "سيارة مع سائق ليوم كامل",
        ],
        "included_en": [
            "Return flights",
            "Three nights with breakfast",
            "Wadis and waterfalls tour",
            "A car with a driver for a full day",
        ],
        "itinerary": [
            (
                "الوصول",
                "Arrival",
                "الاستقبال والاستقرار، ووقت حر مساءً.",
                "Welcome, check-in and a free evening.",
            ),
            (
                "وادي دربات",
                "Wadi Darbat",
                "الشلالات والبحيرات والمروج الخضراء.",
                "The waterfalls, the lakes and the green meadows.",
            ),
            (
                "المغسيل وطاقة",
                "Mughsail and Taqah",
                "الشواطئ والنافورات الطبيعية.",
                "The beaches and the natural blowholes.",
            ),
            (
                "المغادرة",
                "Departure",
                "سوق الحصن ثم التوصيل إلى المطار.",
                "Al Husn souq, then a transfer to the airport.",
            ),
        ],
    },
]


class Command(BaseCommand):
    help = (
        "Fill the demo packages with descriptions, included services and a daily "
        "programme, so the package detail page can be seen fully populated. "
        "Demonstration content only — everything it writes is editable in the panel."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run even when DEBUG is off. This overwrites content, so be sure.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # This overwrites whatever is in those rows. Outside development that is
        # someone's real content, so it takes an explicit flag to get there.
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "DEBUG is off. This command overwrites package content — "
                "re-run with --force if that is genuinely what you want."
            )

        categories = {
            key: PackageCategory.objects.get_or_create(
                slug=key, defaults={"name_ar": names[0], "name_en": names[1]}
            )[0]
            for key, names in CATEGORIES.items()
        }

        written = 0
        for spec in PACKAGES:
            destination = Destination.objects.filter(slug=spec["destination"]).first()
            if destination is None:
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping {spec['slug']}: no destination '{spec['destination']}'."
                    )
                )
                continue

            package, _ = Package.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "title_ar": spec["title_ar"],
                    "title_en": spec["title_en"],
                    "category": categories[spec["category"]],
                    "destination": destination,
                    "description_ar": spec["description_ar"],
                    "description_en": spec["description_en"],
                    "duration_days": spec["duration_days"],
                    "price_from": spec["price_from"],
                    "cover_image": spec["cover_image"],
                    "included_services_ar": "\n".join(spec["included_ar"]),
                    "included_services_en": "\n".join(spec["included_en"]),
                    "is_featured": spec["is_featured"],
                    "is_active": True,
                },
            )

            for index, (title_ar, title_en, body_ar, body_en) in enumerate(
                spec["itinerary"], start=1
            ):
                PackageItinerary.objects.update_or_create(
                    package=package,
                    day_number=index,
                    defaults={
                        "title_ar": title_ar,
                        "title_en": title_en,
                        "description_ar": body_ar,
                        "description_en": body_en,
                    },
                )
            # A shortened programme must not leave orphan days behind from a
            # previous run.
            package.itinerary.filter(day_number__gt=len(spec["itinerary"])).delete()

            written += 1
            self.stdout.write(
                f"{spec['slug']}: {len(spec['itinerary'])} days, "
                f"{len(spec['included_en'])} inclusions"
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {written} package(s)."))

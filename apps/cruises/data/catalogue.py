"""The shipped cruise-port catalogue.

Reference data: the port, the city it serves, and the country it sits in.
Nothing here asserts anything about the company — no sailings, no prices, no
cruise line relationships — so it is safe to ship and safe to re-apply.

Each row is:
    (code, name_en, name_ar, city_en, city_ar, country_en, country_ar, cc)

The homepage asks for a country and then one of its ports, so the country
columns are what group the list. They are spelt the way the airport catalogue
and the panel's country picker spell them, which is how a country ends up with
one group rather than two.

`POPULAR` is what the picker offers before anyone types: where this market
sails from, then the home ports its travellers fly out to join.
"""

POPULAR = (
    "jeddah",
    "dubai-port-rashid",
    "abu-dhabi-zayed",
    "doha",
    "bahrain",
    "muscat",
    "aqaba",
    "barcelona",
    "civitavecchia",
    "istanbul-port",
    "piraeus",
    "singapore-port",
)

# One port per line. `ruff format` would give every field its own line and turn
# a readable table into column soup; the project lints with `ruff check`
# (E501 off) and does not run the formatter.
# fmt: off
PORTS: tuple[tuple[str, str, str, str, str, str, str, str], ...] = (
    ("jeddah", "Jeddah Islamic Port", "ميناء جدة الإسلامي", "Jeddah", "جدة", "Saudi Arabia", "السعودية", "SA"),
    ("yanbu", "Yanbu Commercial Port", "ميناء ينبع التجاري", "Yanbu", "ينبع", "Saudi Arabia", "السعودية", "SA"),
    ("dammam", "King Abdulaziz Port", "ميناء الملك عبدالعزيز", "Dammam", "الدمام", "Saudi Arabia", "السعودية", "SA"),
    ("dubai-port-rashid", "Port Rashid", "ميناء راشد", "Dubai", "دبي", "United Arab Emirates", "الإمارات", "AE"),
    ("abu-dhabi-zayed", "Zayed Port", "ميناء زايد", "Abu Dhabi", "أبوظبي", "United Arab Emirates", "الإمارات", "AE"),
    ("sir-bani-yas", "Sir Bani Yas Island", "جزيرة صير بني ياس", "Sir Bani Yas", "صير بني ياس", "United Arab Emirates", "الإمارات", "AE"),
    ("doha", "Doha Port", "ميناء الدوحة", "Doha", "الدوحة", "Qatar", "قطر", "QA"),
    ("bahrain", "Khalifa Bin Salman Port", "ميناء خليفة بن سلمان", "Manama", "المنامة", "Bahrain", "البحرين", "BH"),
    ("kuwait", "Shuwaikh Port", "ميناء الشويخ", "Kuwait City", "مدينة الكويت", "Kuwait", "الكويت", "KW"),
    ("muscat", "Sultan Qaboos Port", "ميناء السلطان قابوس", "Muscat", "مسقط", "Oman", "عُمان", "OM"),
    ("salalah", "Port of Salalah", "ميناء صلالة", "Salalah", "صلالة", "Oman", "عُمان", "OM"),
    ("khasab", "Khasab Port", "ميناء خصب", "Khasab", "خصب", "Oman", "عُمان", "OM"),
    ("aqaba", "Port of Aqaba", "ميناء العقبة", "Aqaba", "العقبة", "Jordan", "الأردن", "JO"),
    ("sharm", "Sharm El Sheikh Port", "ميناء شرم الشيخ", "Sharm El Sheikh", "شرم الشيخ", "Egypt", "مصر", "EG"),
    ("safaga", "Port Safaga", "ميناء سفاجا", "Safaga", "سفاجا", "Egypt", "مصر", "EG"),
    ("alexandria", "Port of Alexandria", "ميناء الإسكندرية", "Alexandria", "الإسكندرية", "Egypt", "مصر", "EG"),
    ("port-said", "Port Said", "بورسعيد", "Port Said", "بورسعيد", "Egypt", "مصر", "EG"),
    ("barcelona", "Port of Barcelona", "ميناء برشلونة", "Barcelona", "برشلونة", "Spain", "إسبانيا", "ES"),
    ("palma", "Port of Palma", "ميناء بالما", "Palma de Mallorca", "بالما دي مايوركا", "Spain", "إسبانيا", "ES"),
    ("valencia-port", "Port of Valencia", "ميناء فالنسيا", "Valencia", "فالنسيا", "Spain", "إسبانيا", "ES"),
    ("malaga-port", "Port of Málaga", "ميناء مالقة", "Málaga", "مالقة", "Spain", "إسبانيا", "ES"),
    ("ibiza-port", "Port of Ibiza", "ميناء إيبيزا", "Ibiza", "إيبيزا", "Spain", "إسبانيا", "ES"),
    ("tenerife-port", "Santa Cruz de Tenerife", "سانتا كروث دي تينيريفي", "Tenerife", "تينيريفي", "Spain", "إسبانيا", "ES"),
    ("civitavecchia", "Civitavecchia (Rome)", "تشيفيتافيكيا (روما)", "Rome", "روما", "Italy", "إيطاليا", "IT"),
    ("genoa", "Port of Genoa", "ميناء جنوة", "Genoa", "جنوة", "Italy", "إيطاليا", "IT"),
    ("naples", "Port of Naples", "ميناء نابولي", "Naples", "نابولي", "Italy", "إيطاليا", "IT"),
    ("venice", "Port of Venice", "ميناء البندقية", "Venice", "البندقية", "Italy", "إيطاليا", "IT"),
    ("trieste", "Port of Trieste", "ميناء تريستي", "Trieste", "تريستي", "Italy", "إيطاليا", "IT"),
    ("savona", "Port of Savona", "ميناء سافونا", "Savona", "سافونا", "Italy", "إيطاليا", "IT"),
    ("palermo", "Port of Palermo", "ميناء باليرمو", "Palermo", "باليرمو", "Italy", "إيطاليا", "IT"),
    ("bari", "Port of Bari", "ميناء باري", "Bari", "باري", "Italy", "إيطاليا", "IT"),
    ("marseille-port", "Port of Marseille", "ميناء مرسيليا", "Marseille", "مرسيليا", "France", "فرنسا", "FR"),
    ("nice-port", "Port of Nice", "ميناء نيس", "Nice", "نيس", "France", "فرنسا", "FR"),
    ("ajaccio", "Port of Ajaccio", "ميناء أجاكسيو", "Ajaccio", "أجاكسيو", "France", "فرنسا", "FR"),
    ("monaco-port", "Port Hercule", "ميناء هرقل", "Monaco", "موناكو", "Monaco", "موناكو", "MC"),
    ("valletta", "Grand Harbour", "الميناء الكبير", "Valletta", "فاليتا", "Malta", "مالطا", "MT"),
    ("lisbon-port", "Port of Lisbon", "ميناء لشبونة", "Lisbon", "لشبونة", "Portugal", "البرتغال", "PT"),
    ("funchal", "Port of Funchal", "ميناء فونشال", "Madeira", "ماديرا", "Portugal", "البرتغال", "PT"),
    ("casablanca-port", "Port of Casablanca", "ميناء الدار البيضاء", "Casablanca", "الدار البيضاء", "Morocco", "المغرب", "MA"),
    ("tangier-port", "Tanger Ville", "ميناء طنجة المدينة", "Tangier", "طنجة", "Morocco", "المغرب", "MA"),
    ("tunis-port", "La Goulette", "حلق الوادي", "Tunis", "تونس", "Tunisia", "تونس", "TN"),
    ("piraeus", "Port of Piraeus (Athens)", "ميناء بيرايوس (أثينا)", "Athens", "أثينا", "Greece", "اليونان", "GR"),
    ("santorini-port", "Santorini Port", "ميناء سانتوريني", "Santorini", "سانتوريني", "Greece", "اليونان", "GR"),
    ("mykonos-port", "Mykonos Port", "ميناء ميكونوس", "Mykonos", "ميكونوس", "Greece", "اليونان", "GR"),
    ("rhodes-port", "Port of Rhodes", "ميناء رودس", "Rhodes", "رودس", "Greece", "اليونان", "GR"),
    ("heraklion-port", "Port of Heraklion", "ميناء هيراكليون", "Crete", "كريت", "Greece", "اليونان", "GR"),
    ("corfu", "Port of Corfu", "ميناء كورفو", "Corfu", "كورفو", "Greece", "اليونان", "GR"),
    ("istanbul-port", "Galataport", "ميناء غلطة", "Istanbul", "إسطنبول", "Türkiye", "تركيا", "TR"),
    ("kusadasi", "Port of Kuşadası", "ميناء كوش أداسي", "Kuşadası", "كوش أداسي", "Türkiye", "تركيا", "TR"),
    ("bodrum-port", "Port of Bodrum", "ميناء بودروم", "Bodrum", "بودروم", "Türkiye", "تركيا", "TR"),
    ("izmir-port", "Port of İzmir", "ميناء إزمير", "İzmir", "إزمير", "Türkiye", "تركيا", "TR"),
    ("dubrovnik-port", "Port of Dubrovnik", "ميناء دوبروفنيك", "Dubrovnik", "دوبروفنيك", "Croatia", "كرواتيا", "HR"),
    ("split-port", "Port of Split", "ميناء سبليت", "Split", "سبليت", "Croatia", "كرواتيا", "HR"),
    ("kotor", "Port of Kotor", "ميناء كوتور", "Kotor", "كوتور", "Montenegro", "الجبل الأسود", "ME"),
    ("limassol", "Port of Limassol", "ميناء ليماسول", "Limassol", "ليماسول", "Cyprus", "قبرص", "CY"),
    ("southampton", "Port of Southampton", "ميناء ساوثهامبتون", "Southampton", "ساوثهامبتون", "United Kingdom", "المملكة المتحدة", "GB"),
    ("dover", "Port of Dover", "ميناء دوفر", "Dover", "دوفر", "United Kingdom", "المملكة المتحدة", "GB"),
    ("edinburgh-port", "Port of Leith", "ميناء ليث", "Edinburgh", "إدنبرة", "United Kingdom", "المملكة المتحدة", "GB"),
    ("amsterdam-port", "Passenger Terminal Amsterdam", "محطة ركاب أمستردام", "Amsterdam", "أمستردام", "Netherlands", "هولندا", "NL"),
    ("rotterdam", "Port of Rotterdam", "ميناء روتردام", "Rotterdam", "روتردام", "Netherlands", "هولندا", "NL"),
    ("hamburg-port", "Port of Hamburg", "ميناء هامبورغ", "Hamburg", "هامبورغ", "Germany", "ألمانيا", "DE"),
    ("kiel", "Port of Kiel", "ميناء كيل", "Kiel", "كيل", "Germany", "ألمانيا", "DE"),
    ("copenhagen-port", "Port of Copenhagen", "ميناء كوبنهاغن", "Copenhagen", "كوبنهاغن", "Denmark", "الدنمارك", "DK"),
    ("stockholm-port", "Port of Stockholm", "ميناء ستوكهولم", "Stockholm", "ستوكهولم", "Sweden", "السويد", "SE"),
    ("helsinki-port", "Port of Helsinki", "ميناء هلسنكي", "Helsinki", "هلسنكي", "Finland", "فنلندا", "FI"),
    ("oslo-port", "Port of Oslo", "ميناء أوسلو", "Oslo", "أوسلو", "Norway", "النرويج", "NO"),
    ("bergen", "Port of Bergen", "ميناء بيرغن", "Bergen", "بيرغن", "Norway", "النرويج", "NO"),
    ("tromso", "Port of Tromsø", "ميناء ترومسو", "Tromsø", "ترومسو", "Norway", "النرويج", "NO"),
    ("reykjavik-port", "Port of Reykjavík", "ميناء ريكيافيك", "Reykjavík", "ريكيافيك", "Iceland", "آيسلندا", "IS"),
    ("dublin-port", "Dublin Port", "ميناء دبلن", "Dublin", "دبلن", "Ireland", "أيرلندا", "IE"),
    ("miami", "PortMiami", "ميناء ميامي", "Miami", "ميامي", "United States", "الولايات المتحدة", "US"),
    ("fort-lauderdale", "Port Everglades", "ميناء إيفرغليدز", "Fort Lauderdale", "فورت لودرديل", "United States", "الولايات المتحدة", "US"),
    ("port-canaveral", "Port Canaveral", "ميناء كانافيرال", "Orlando", "أورلاندو", "United States", "الولايات المتحدة", "US"),
    ("tampa", "Port Tampa Bay", "ميناء تامبا", "Tampa", "تامبا", "United States", "الولايات المتحدة", "US"),
    ("galveston", "Port of Galveston", "ميناء غالفستون", "Galveston", "غالفستون", "United States", "الولايات المتحدة", "US"),
    ("new-york-port", "Manhattan Cruise Terminal", "محطة مانهاتن للرحلات البحرية", "New York", "نيويورك", "United States", "الولايات المتحدة", "US"),
    ("seattle-port", "Port of Seattle", "ميناء سياتل", "Seattle", "سياتل", "United States", "الولايات المتحدة", "US"),
    ("los-angeles-port", "Port of Los Angeles", "ميناء لوس أنجلوس", "Los Angeles", "لوس أنجلوس", "United States", "الولايات المتحدة", "US"),
    ("san-juan", "Port of San Juan", "ميناء سان خوان", "San Juan", "سان خوان", "Puerto Rico", "بورتوريكو", "PR"),
    ("nassau", "Port of Nassau", "ميناء ناسو", "Nassau", "ناسو", "Bahamas", "جزر البهاما", "BS"),
    ("bridgetown", "Bridgetown Port", "ميناء بريدجتاون", "Bridgetown", "بريدجتاون", "Barbados", "بربادوس", "BB"),
    ("cozumel", "Port of Cozumel", "ميناء كوزوميل", "Cozumel", "كوزوميل", "Mexico", "المكسيك", "MX"),
    ("vancouver-port", "Canada Place", "كندا بليس", "Vancouver", "فانكوفر", "Canada", "كندا", "CA"),
    ("montreal-port", "Port of Montréal", "ميناء مونتريال", "Montréal", "مونتريال", "Canada", "كندا", "CA"),
    ("singapore-port", "Marina Bay Cruise Centre", "مركز مارينا باي للرحلات البحرية", "Singapore", "سنغافورة", "Singapore", "سنغافورة", "SG"),
    ("hong-kong-port", "Kai Tak Cruise Terminal", "محطة كاي تاك للرحلات البحرية", "Hong Kong", "هونغ كونغ", "Hong Kong", "هونغ كونغ", "HK"),
    ("shanghai-port", "Wusongkou Cruise Terminal", "محطة ووسونغكو للرحلات البحرية", "Shanghai", "شانغهاي", "China", "الصين", "CN"),
    ("yokohama", "Port of Yokohama", "ميناء يوكوهاما", "Yokohama", "يوكوهاما", "Japan", "اليابان", "JP"),
    ("kobe", "Port of Kobe", "ميناء كوبي", "Kobe", "كوبي", "Japan", "اليابان", "JP"),
    ("busan-port", "Port of Busan", "ميناء بوسان", "Busan", "بوسان", "South Korea", "كوريا الجنوبية", "KR"),
    ("phuket-port", "Phuket Cruise Port", "ميناء فوكيت", "Phuket", "فوكيت", "Thailand", "تايلاند", "TH"),
    ("laem-chabang", "Laem Chabang (Bangkok)", "ليم تشابانغ (بانكوك)", "Bangkok", "بانكوك", "Thailand", "تايلاند", "TH"),
    ("port-klang", "Port Klang (Kuala Lumpur)", "ميناء كلانغ (كوالالمبور)", "Kuala Lumpur", "كوالالمبور", "Malaysia", "ماليزيا", "MY"),
    ("benoa", "Benoa Harbour (Bali)", "ميناء بينوا (بالي)", "Bali", "بالي", "Indonesia", "إندونيسيا", "ID"),
    ("mumbai-port", "Mumbai Cruise Terminal", "محطة مومباي للرحلات البحرية", "Mumbai", "مومباي", "India", "الهند", "IN"),
    ("colombo-port", "Port of Colombo", "ميناء كولومبو", "Colombo", "كولومبو", "Sri Lanka", "سريلانكا", "LK"),
    ("male-port", "Port of Malé", "ميناء ماليه", "Malé", "ماليه", "Maldives", "المالديف", "MV"),
    ("sydney-port", "Overseas Passenger Terminal", "محطة الركاب الدولية", "Sydney", "سيدني", "Australia", "أستراليا", "AU"),
    ("auckland-port", "Port of Auckland", "ميناء أوكلاند", "Auckland", "أوكلاند", "New Zealand", "نيوزيلندا", "NZ"),
    ("cape-town-port", "Port of Cape Town", "ميناء كيب تاون", "Cape Town", "كيب تاون", "South Africa", "جنوب أفريقيا", "ZA"),
    ("durban-port", "Port of Durban", "ميناء ديربان", "Durban", "ديربان", "South Africa", "جنوب أفريقيا", "ZA"),
    ("mombasa", "Port of Mombasa", "ميناء مومباسا", "Mombasa", "مومباسا", "Kenya", "كينيا", "KE"),
    ("zanzibar-port", "Port of Zanzibar", "ميناء زنجبار", "Zanzibar", "زنجبار", "Tanzania", "تنزانيا", "TZ"),
    ("port-louis", "Port Louis", "بورت لويس", "Port Louis", "بورت لويس", "Mauritius", "موريشيوس", "MU"),
    ("victoria-sc", "Port Victoria", "ميناء فيكتوريا", "Victoria", "فيكتوريا", "Seychelles", "سيشل", "SC"),
)
# fmt: on


def sync(CruisePort):
    """Load or refresh the catalogue. Safe to re-run.

    Matched on `code`, so re-running updates a port in place rather than
    duplicating it — and an editor's own row, added in the panel with a code of
    its own, is left alone.
    """
    created = updated = 0
    for order, (code, name_en, name_ar, city_en, city_ar, country_en, country_ar, cc) in enumerate(
        PORTS
    ):
        _, was_created = CruisePort.objects.update_or_create(
            code=code,
            defaults={
                "name_en": name_en,
                "name_ar": name_ar,
                "city_en": city_en,
                "city_ar": city_ar,
                "country_en": country_en,
                "country_ar": country_ar,
                "country_code": cc,
                "is_popular": code in POPULAR,
                "order": POPULAR.index(code) if code in POPULAR else order + 100,
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return created, updated

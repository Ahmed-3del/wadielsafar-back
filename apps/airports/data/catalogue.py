"""The shipped airport catalogue.

Reference data: IATA code, airport name, city and country. Nothing here asserts
anything about the company — no routes, no prices, no airline relationships —
so it is safe to ship and safe to re-apply.

Each row is:
    (iata, name_en, name_ar, city_en, city_ar, country_en, country_ar, cc)

`POPULAR` lists the codes the picker offers before the traveller types: Saudi
departure points first, then the destinations most asked for from here.
"""

POPULAR = ("JED", "RUH", "DMM", "MED", "DXB", "DOH", "CAI", "IST", "LHR", "KUL", "BKK", "AMM")

# One airport per line. `ruff format` would give each field its own line and
# turn a 190-line table into 1,500 lines of unreadable column soup; the
# project lints with `ruff check` (E501 off) and does not run the formatter.
# fmt: off
AIRPORTS: tuple[tuple[str, str, str, str, str, str, str, str], ...] = (
    # ---- Saudi Arabia -----------------------------------------------------
    ("JED", "King Abdulaziz International Airport", "مطار الملك عبدالعزيز الدولي", "Jeddah", "جدة", "Saudi Arabia", "السعودية", "SA"),
    ("RUH", "King Khalid International Airport", "مطار الملك خالد الدولي", "Riyadh", "الرياض", "Saudi Arabia", "السعودية", "SA"),
    ("DMM", "King Fahd International Airport", "مطار الملك فهد الدولي", "Dammam", "الدمام", "Saudi Arabia", "السعودية", "SA"),
    ("MED", "Prince Mohammad bin Abdulaziz International Airport", "مطار الأمير محمد بن عبدالعزيز الدولي", "Madinah", "المدينة المنورة", "Saudi Arabia", "السعودية", "SA"),
    ("AHB", "Abha International Airport", "مطار أبها الدولي", "Abha", "أبها", "Saudi Arabia", "السعودية", "SA"),
    ("TIF", "Taif International Airport", "مطار الطائف الدولي", "Taif", "الطائف", "Saudi Arabia", "السعودية", "SA"),
    ("ELQ", "Prince Nayef bin Abdulaziz Regional Airport", "مطار الأمير نايف بن عبدالعزيز الإقليمي", "Qassim", "القصيم", "Saudi Arabia", "السعودية", "SA"),
    ("GIZ", "Jazan King Abdullah bin Abdulaziz Airport", "مطار جازان الملك عبدالله بن عبدالعزيز", "Jazan", "جازان", "Saudi Arabia", "السعودية", "SA"),
    ("TUU", "Tabuk Airport", "مطار تبوك", "Tabuk", "تبوك", "Saudi Arabia", "السعودية", "SA"),
    ("YNB", "Yanbu Airport", "مطار ينبع", "Yanbu", "ينبع", "Saudi Arabia", "السعودية", "SA"),
    ("HAS", "Hail Airport", "مطار حائل", "Hail", "حائل", "Saudi Arabia", "السعودية", "SA"),
    ("EAM", "Najran Airport", "مطار نجران", "Najran", "نجران", "Saudi Arabia", "السعودية", "SA"),
    ("AJF", "Al-Jouf Airport", "مطار الجوف", "Sakaka", "سكاكا", "Saudi Arabia", "السعودية", "SA"),
    ("ABT", "Al-Baha Airport", "مطار الباحة", "Al Baha", "الباحة", "Saudi Arabia", "السعودية", "SA"),
    ("BHH", "Bisha Airport", "مطار بيشة", "Bisha", "بيشة", "Saudi Arabia", "السعودية", "SA"),
    ("SHW", "Sharurah Airport", "مطار شرورة", "Sharurah", "شرورة", "Saudi Arabia", "السعودية", "SA"),
    ("EJH", "Al Wajh Airport", "مطار الوجه", "Al Wajh", "الوجه", "Saudi Arabia", "السعودية", "SA"),
    ("URY", "Gurayat Domestic Airport", "مطار القريات", "Gurayat", "القريات", "Saudi Arabia", "السعودية", "SA"),
    ("RAH", "Rafha Domestic Airport", "مطار رفحاء", "Rafha", "رفحاء", "Saudi Arabia", "السعودية", "SA"),
    ("RAE", "Arar Airport", "مطار عرعر", "Arar", "عرعر", "Saudi Arabia", "السعودية", "SA"),
    ("AQI", "Al Qaisumah/Hafar Al-Batin Airport", "مطار القيصومة/حفر الباطن", "Hafar Al-Batin", "حفر الباطن", "Saudi Arabia", "السعودية", "SA"),
    ("HOF", "Al-Ahsa International Airport", "مطار الأحساء الدولي", "Al-Ahsa", "الأحساء", "Saudi Arabia", "السعودية", "SA"),
    ("TUI", "Turaif Domestic Airport", "مطار طريف", "Turaif", "طريف", "Saudi Arabia", "السعودية", "SA"),
    ("ULH", "Prince Abdul Majeed bin Abdulaziz Airport", "مطار الأمير عبدالمجيد بن عبدالعزيز", "AlUla", "العلا", "Saudi Arabia", "السعودية", "SA"),
    ("WAE", "Wadi Al-Dawasir Airport", "مطار وادي الدواسر", "Wadi Al-Dawasir", "وادي الدواسر", "Saudi Arabia", "السعودية", "SA"),
    ("NUM", "Neom Bay Airport", "مطار خليج نيوم", "Neom", "نيوم", "Saudi Arabia", "السعودية", "SA"),
    ("KMX", "King Khalid Air Base", "قاعدة الملك خالد الجوية", "Khamis Mushait", "خميس مشيط", "Saudi Arabia", "السعودية", "SA"),
    ("DWD", "Dawadmi Domestic Airport", "مطار الدوادمي", "Dawadmi", "الدوادمي", "Saudi Arabia", "السعودية", "SA"),
    # ---- Gulf -------------------------------------------------------------
    ("DXB", "Dubai International Airport", "مطار دبي الدولي", "Dubai", "دبي", "United Arab Emirates", "الإمارات", "AE"),
    ("DWC", "Al Maktoum International Airport", "مطار آل مكتوم الدولي", "Dubai", "دبي", "United Arab Emirates", "الإمارات", "AE"),
    ("AUH", "Zayed International Airport", "مطار زايد الدولي", "Abu Dhabi", "أبوظبي", "United Arab Emirates", "الإمارات", "AE"),
    ("SHJ", "Sharjah International Airport", "مطار الشارقة الدولي", "Sharjah", "الشارقة", "United Arab Emirates", "الإمارات", "AE"),
    ("RKT", "Ras Al Khaimah International Airport", "مطار رأس الخيمة الدولي", "Ras Al Khaimah", "رأس الخيمة", "United Arab Emirates", "الإمارات", "AE"),
    ("DOH", "Hamad International Airport", "مطار حمد الدولي", "Doha", "الدوحة", "Qatar", "قطر", "QA"),
    ("KWI", "Kuwait International Airport", "مطار الكويت الدولي", "Kuwait City", "مدينة الكويت", "Kuwait", "الكويت", "KW"),
    ("BAH", "Bahrain International Airport", "مطار البحرين الدولي", "Manama", "المنامة", "Bahrain", "البحرين", "BH"),
    ("MCT", "Muscat International Airport", "مطار مسقط الدولي", "Muscat", "مسقط", "Oman", "عُمان", "OM"),
    ("SLL", "Salalah International Airport", "مطار صلالة الدولي", "Salalah", "صلالة", "Oman", "عُمان", "OM"),
    # ---- Levant, Egypt, North Africa --------------------------------------
    ("AMM", "Queen Alia International Airport", "مطار الملكة علياء الدولي", "Amman", "عمّان", "Jordan", "الأردن", "JO"),
    ("AQJ", "King Hussein International Airport", "مطار الملك الحسين الدولي", "Aqaba", "العقبة", "Jordan", "الأردن", "JO"),
    ("BEY", "Beirut–Rafic Hariri International Airport", "مطار بيروت رفيق الحريري الدولي", "Beirut", "بيروت", "Lebanon", "لبنان", "LB"),
    ("CAI", "Cairo International Airport", "مطار القاهرة الدولي", "Cairo", "القاهرة", "Egypt", "مصر", "EG"),
    ("HBE", "Borg El Arab Airport", "مطار برج العرب", "Alexandria", "الإسكندرية", "Egypt", "مصر", "EG"),
    ("HRG", "Hurghada International Airport", "مطار الغردقة الدولي", "Hurghada", "الغردقة", "Egypt", "مصر", "EG"),
    ("SSH", "Sharm El Sheikh International Airport", "مطار شرم الشيخ الدولي", "Sharm El Sheikh", "شرم الشيخ", "Egypt", "مصر", "EG"),
    ("LXR", "Luxor International Airport", "مطار الأقصر الدولي", "Luxor", "الأقصر", "Egypt", "مصر", "EG"),
    ("ASW", "Aswan International Airport", "مطار أسوان الدولي", "Aswan", "أسوان", "Egypt", "مصر", "EG"),
    ("TUN", "Tunis–Carthage International Airport", "مطار تونس قرطاج الدولي", "Tunis", "تونس", "Tunisia", "تونس", "TN"),
    ("CMN", "Mohammed V International Airport", "مطار محمد الخامس الدولي", "Casablanca", "الدار البيضاء", "Morocco", "المغرب", "MA"),
    ("RAK", "Marrakesh Menara Airport", "مطار مراكش المنارة", "Marrakesh", "مراكش", "Morocco", "المغرب", "MA"),
    ("TNG", "Tangier Ibn Battouta Airport", "مطار طنجة ابن بطوطة", "Tangier", "طنجة", "Morocco", "المغرب", "MA"),
    ("ALG", "Houari Boumediene Airport", "مطار هواري بومدين", "Algiers", "الجزائر", "Algeria", "الجزائر", "DZ"),
    # ---- Türkiye ----------------------------------------------------------
    ("IST", "Istanbul Airport", "مطار إسطنبول", "Istanbul", "إسطنبول", "Türkiye", "تركيا", "TR"),
    ("SAW", "Sabiha Gökçen International Airport", "مطار صبيحة كوكجن الدولي", "Istanbul", "إسطنبول", "Türkiye", "تركيا", "TR"),
    ("AYT", "Antalya Airport", "مطار أنطاليا", "Antalya", "أنطاليا", "Türkiye", "تركيا", "TR"),
    ("ADB", "İzmir Adnan Menderes Airport", "مطار إزمير عدنان مندريس", "İzmir", "إزمير", "Türkiye", "تركيا", "TR"),
    ("ESB", "Ankara Esenboğa Airport", "مطار أنقرة إيسنبوغا", "Ankara", "أنقرة", "Türkiye", "تركيا", "TR"),
    ("BJV", "Milas–Bodrum Airport", "مطار ميلاس بودروم", "Bodrum", "بودروم", "Türkiye", "تركيا", "TR"),
    ("TZX", "Trabzon Airport", "مطار طرابزون", "Trabzon", "طرابزون", "Türkiye", "تركيا", "TR"),
    # ---- Iraq -------------------------------------------------------------
    ("BGW", "Baghdad International Airport", "مطار بغداد الدولي", "Baghdad", "بغداد", "Iraq", "العراق", "IQ"),
    ("EBL", "Erbil International Airport", "مطار أربيل الدولي", "Erbil", "أربيل", "Iraq", "العراق", "IQ"),
    ("NJF", "Al Najaf International Airport", "مطار النجف الدولي", "Najaf", "النجف", "Iraq", "العراق", "IQ"),
    ("BSR", "Basra International Airport", "مطار البصرة الدولي", "Basra", "البصرة", "Iraq", "العراق", "IQ"),
    # ---- United Kingdom & Ireland -----------------------------------------
    ("LHR", "London Heathrow Airport", "مطار لندن هيثرو", "London", "لندن", "United Kingdom", "المملكة المتحدة", "GB"),
    ("LGW", "London Gatwick Airport", "مطار لندن جاتويك", "London", "لندن", "United Kingdom", "المملكة المتحدة", "GB"),
    ("MAN", "Manchester Airport", "مطار مانشستر", "Manchester", "مانشستر", "United Kingdom", "المملكة المتحدة", "GB"),
    ("BHX", "Birmingham Airport", "مطار برمنغهام", "Birmingham", "برمنغهام", "United Kingdom", "المملكة المتحدة", "GB"),
    ("EDI", "Edinburgh Airport", "مطار إدنبرة", "Edinburgh", "إدنبرة", "United Kingdom", "المملكة المتحدة", "GB"),
    ("DUB", "Dublin Airport", "مطار دبلن", "Dublin", "دبلن", "Ireland", "أيرلندا", "IE"),
    # ---- Western Europe ----------------------------------------------------
    ("CDG", "Paris Charles de Gaulle Airport", "مطار باريس شارل ديغول", "Paris", "باريس", "France", "فرنسا", "FR"),
    ("ORY", "Paris Orly Airport", "مطار باريس أورلي", "Paris", "باريس", "France", "فرنسا", "FR"),
    ("NCE", "Nice Côte d'Azur Airport", "مطار نيس كوت دازور", "Nice", "نيس", "France", "فرنسا", "FR"),
    ("LYS", "Lyon–Saint Exupéry Airport", "مطار ليون سان إكزوبيري", "Lyon", "ليون", "France", "فرنسا", "FR"),
    ("FRA", "Frankfurt Airport", "مطار فرانكفورت", "Frankfurt", "فرانكفورت", "Germany", "ألمانيا", "DE"),
    ("MUC", "Munich Airport", "مطار ميونخ", "Munich", "ميونخ", "Germany", "ألمانيا", "DE"),
    ("BER", "Berlin Brandenburg Airport", "مطار برلين براندنبورغ", "Berlin", "برلين", "Germany", "ألمانيا", "DE"),
    ("DUS", "Düsseldorf Airport", "مطار دوسلدورف", "Düsseldorf", "دوسلدورف", "Germany", "ألمانيا", "DE"),
    ("HAM", "Hamburg Airport", "مطار هامبورغ", "Hamburg", "هامبورغ", "Germany", "ألمانيا", "DE"),
    ("AMS", "Amsterdam Airport Schiphol", "مطار أمستردام سخيبول", "Amsterdam", "أمستردام", "Netherlands", "هولندا", "NL"),
    ("BRU", "Brussels Airport", "مطار بروكسل", "Brussels", "بروكسل", "Belgium", "بلجيكا", "BE"),
    ("ZRH", "Zurich Airport", "مطار زيورخ", "Zurich", "زيورخ", "Switzerland", "سويسرا", "CH"),
    ("GVA", "Geneva Airport", "مطار جنيف", "Geneva", "جنيف", "Switzerland", "سويسرا", "CH"),
    ("VIE", "Vienna International Airport", "مطار فيينا الدولي", "Vienna", "فيينا", "Austria", "النمسا", "AT"),
    ("MAD", "Adolfo Suárez Madrid–Barajas Airport", "مطار مدريد باراخاس", "Madrid", "مدريد", "Spain", "إسبانيا", "ES"),
    ("BCN", "Josep Tarradellas Barcelona–El Prat Airport", "مطار برشلونة البرات", "Barcelona", "برشلونة", "Spain", "إسبانيا", "ES"),
    ("AGP", "Málaga–Costa del Sol Airport", "مطار مالقة", "Málaga", "مالقة", "Spain", "إسبانيا", "ES"),
    ("LIS", "Lisbon Airport", "مطار لشبونة", "Lisbon", "لشبونة", "Portugal", "البرتغال", "PT"),
    ("OPO", "Francisco Sá Carneiro Airport", "مطار بورتو", "Porto", "بورتو", "Portugal", "البرتغال", "PT"),
    ("FCO", "Rome Fiumicino Airport", "مطار روما فيوميتشينو", "Rome", "روما", "Italy", "إيطاليا", "IT"),
    ("MXP", "Milan Malpensa Airport", "مطار ميلانو مالبينسا", "Milan", "ميلانو", "Italy", "إيطاليا", "IT"),
    ("VCE", "Venice Marco Polo Airport", "مطار البندقية ماركو بولو", "Venice", "البندقية", "Italy", "إيطاليا", "IT"),
    ("NAP", "Naples International Airport", "مطار نابولي الدولي", "Naples", "نابولي", "Italy", "إيطاليا", "IT"),
    ("ATH", "Athens International Airport", "مطار أثينا الدولي", "Athens", "أثينا", "Greece", "اليونان", "GR"),
    # ---- Central, Northern & Eastern Europe -------------------------------
    ("PRG", "Václav Havel Airport Prague", "مطار براغ", "Prague", "براغ", "Czechia", "التشيك", "CZ"),
    ("BUD", "Budapest Ferenc Liszt International Airport", "مطار بودابست", "Budapest", "بودابست", "Hungary", "المجر", "HU"),
    ("WAW", "Warsaw Chopin Airport", "مطار وارسو شوبان", "Warsaw", "وارسو", "Poland", "بولندا", "PL"),
    ("CPH", "Copenhagen Airport", "مطار كوبنهاغن", "Copenhagen", "كوبنهاغن", "Denmark", "الدنمارك", "DK"),
    ("ARN", "Stockholm Arlanda Airport", "مطار ستوكهولم أرلاندا", "Stockholm", "ستوكهولم", "Sweden", "السويد", "SE"),
    ("OSL", "Oslo Airport, Gardermoen", "مطار أوسلو", "Oslo", "أوسلو", "Norway", "النرويج", "NO"),
    ("HEL", "Helsinki-Vantaa Airport", "مطار هلسنكي", "Helsinki", "هلسنكي", "Finland", "فنلندا", "FI"),
    ("SVO", "Sheremetyevo International Airport", "مطار شيريميتيفو الدولي", "Moscow", "موسكو", "Russia", "روسيا", "RU"),
    ("SJJ", "Sarajevo International Airport", "مطار سراييفو الدولي", "Sarajevo", "سراييفو", "Bosnia and Herzegovina", "البوسنة والهرسك", "BA"),
    ("TBS", "Tbilisi International Airport", "مطار تبليسي الدولي", "Tbilisi", "تبليسي", "Georgia", "جورجيا", "GE"),
    ("GYD", "Heydar Aliyev International Airport", "مطار حيدر علييف الدولي", "Baku", "باكو", "Azerbaijan", "أذربيجان", "AZ"),
    # ---- South & Central Asia ---------------------------------------------
    ("DEL", "Indira Gandhi International Airport", "مطار إنديرا غاندي الدولي", "New Delhi", "نيودلهي", "India", "الهند", "IN"),
    ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "مطار تشاتراباتي شيفاجي الدولي", "Mumbai", "مومباي", "India", "الهند", "IN"),
    ("MAA", "Chennai International Airport", "مطار تشيناي الدولي", "Chennai", "تشيناي", "India", "الهند", "IN"),
    ("COK", "Cochin International Airport", "مطار كوتشين الدولي", "Kochi", "كوتشي", "India", "الهند", "IN"),
    ("HYD", "Rajiv Gandhi International Airport", "مطار راجيف غاندي الدولي", "Hyderabad", "حيدر آباد", "India", "الهند", "IN"),
    ("BLR", "Kempegowda International Airport", "مطار كيمبيغودا الدولي", "Bengaluru", "بنغالورو", "India", "الهند", "IN"),
    ("CCJ", "Calicut International Airport", "مطار كاليكوت الدولي", "Kozhikode", "كوزيكود", "India", "الهند", "IN"),
    ("TRV", "Thiruvananthapuram International Airport", "مطار تيروفانانثابورام الدولي", "Thiruvananthapuram", "تيروفانانثابورام", "India", "الهند", "IN"),
    ("CMB", "Bandaranaike International Airport", "مطار باندارانايكه الدولي", "Colombo", "كولومبو", "Sri Lanka", "سريلانكا", "LK"),
    ("MLE", "Velana International Airport", "مطار فيلانا الدولي", "Malé", "ماليه", "Maldives", "المالديف", "MV"),
    ("KTM", "Tribhuvan International Airport", "مطار تريبهوفان الدولي", "Kathmandu", "كاتماندو", "Nepal", "نيبال", "NP"),
    ("ISB", "Islamabad International Airport", "مطار إسلام آباد الدولي", "Islamabad", "إسلام آباد", "Pakistan", "باكستان", "PK"),
    ("KHI", "Jinnah International Airport", "مطار جناح الدولي", "Karachi", "كراتشي", "Pakistan", "باكستان", "PK"),
    ("LHE", "Allama Iqbal International Airport", "مطار علامة إقبال الدولي", "Lahore", "لاهور", "Pakistan", "باكستان", "PK"),
    ("PEW", "Bacha Khan International Airport", "مطار باشا خان الدولي", "Peshawar", "بيشاور", "Pakistan", "باكستان", "PK"),
    ("SKT", "Sialkot International Airport", "مطار سيالكوت الدولي", "Sialkot", "سيالكوت", "Pakistan", "باكستان", "PK"),
    ("MUX", "Multan International Airport", "مطار ملتان الدولي", "Multan", "ملتان", "Pakistan", "باكستان", "PK"),
    ("DAC", "Hazrat Shahjalal International Airport", "مطار حضرت شاه جلال الدولي", "Dhaka", "دكا", "Bangladesh", "بنغلاديش", "BD"),
    ("CGP", "Shah Amanat International Airport", "مطار شاه أمانت الدولي", "Chattogram", "شيتاغونغ", "Bangladesh", "بنغلاديش", "BD"),
    ("TAS", "Tashkent International Airport", "مطار طشقند الدولي", "Tashkent", "طشقند", "Uzbekistan", "أوزبكستان", "UZ"),
    ("ALA", "Almaty International Airport", "مطار ألماتي الدولي", "Almaty", "ألماتي", "Kazakhstan", "كازاخستان", "KZ"),
    # ---- East & Southeast Asia --------------------------------------------
    ("KUL", "Kuala Lumpur International Airport", "مطار كوالالمبور الدولي", "Kuala Lumpur", "كوالالمبور", "Malaysia", "ماليزيا", "MY"),
    ("SIN", "Singapore Changi Airport", "مطار سنغافورة شانغي", "Singapore", "سنغافورة", "Singapore", "سنغافورة", "SG"),
    ("BKK", "Suvarnabhumi Airport", "مطار سوفارنابومي", "Bangkok", "بانكوك", "Thailand", "تايلاند", "TH"),
    ("DMK", "Don Mueang International Airport", "مطار دون مويانغ الدولي", "Bangkok", "بانكوك", "Thailand", "تايلاند", "TH"),
    ("HKT", "Phuket International Airport", "مطار بوكيت الدولي", "Phuket", "بوكيت", "Thailand", "تايلاند", "TH"),
    ("CNX", "Chiang Mai International Airport", "مطار شيانغ ماي الدولي", "Chiang Mai", "شيانغ ماي", "Thailand", "تايلاند", "TH"),
    ("DPS", "Ngurah Rai International Airport", "مطار نجوراه راي الدولي", "Bali", "بالي", "Indonesia", "إندونيسيا", "ID"),
    ("CGK", "Soekarno–Hatta International Airport", "مطار سوكارنو هاتا الدولي", "Jakarta", "جاكرتا", "Indonesia", "إندونيسيا", "ID"),
    ("HKG", "Hong Kong International Airport", "مطار هونغ كونغ الدولي", "Hong Kong", "هونغ كونغ", "Hong Kong", "هونغ كونغ", "HK"),
    ("ICN", "Incheon International Airport", "مطار إنتشون الدولي", "Seoul", "سيول", "South Korea", "كوريا الجنوبية", "KR"),
    ("NRT", "Narita International Airport", "مطار ناريتا الدولي", "Tokyo", "طوكيو", "Japan", "اليابان", "JP"),
    ("HND", "Tokyo Haneda Airport", "مطار طوكيو هانيدا", "Tokyo", "طوكيو", "Japan", "اليابان", "JP"),
    ("KIX", "Kansai International Airport", "مطار كانساي الدولي", "Osaka", "أوساكا", "Japan", "اليابان", "JP"),
    ("PEK", "Beijing Capital International Airport", "مطار بكين الدولي", "Beijing", "بكين", "China", "الصين", "CN"),
    ("PVG", "Shanghai Pudong International Airport", "مطار شنغهاي بودونغ الدولي", "Shanghai", "شنغهاي", "China", "الصين", "CN"),
    ("CAN", "Guangzhou Baiyun International Airport", "مطار قوانغتشو بايون الدولي", "Guangzhou", "قوانغتشو", "China", "الصين", "CN"),
    ("TPE", "Taiwan Taoyuan International Airport", "مطار تايوان تاويوان الدولي", "Taipei", "تايبيه", "Taiwan", "تايوان", "TW"),
    ("MNL", "Ninoy Aquino International Airport", "مطار نينوي أكينو الدولي", "Manila", "مانيلا", "Philippines", "الفلبين", "PH"),
    # ---- Africa -----------------------------------------------------------
    ("JNB", "O. R. Tambo International Airport", "مطار أو آر تامبو الدولي", "Johannesburg", "جوهانسبرغ", "South Africa", "جنوب أفريقيا", "ZA"),
    ("CPT", "Cape Town International Airport", "مطار كيب تاون الدولي", "Cape Town", "كيب تاون", "South Africa", "جنوب أفريقيا", "ZA"),
    ("NBO", "Jomo Kenyatta International Airport", "مطار جومو كينياتا الدولي", "Nairobi", "نيروبي", "Kenya", "كينيا", "KE"),
    ("ADD", "Addis Ababa Bole International Airport", "مطار أديس أبابا بولي الدولي", "Addis Ababa", "أديس أبابا", "Ethiopia", "إثيوبيا", "ET"),
    ("DAR", "Julius Nyerere International Airport", "مطار جوليوس نيريري الدولي", "Dar es Salaam", "دار السلام", "Tanzania", "تنزانيا", "TZ"),
    ("ZNZ", "Abeid Amani Karume International Airport", "مطار عبيد أماني كرومي الدولي", "Zanzibar", "زنجبار", "Tanzania", "تنزانيا", "TZ"),
    ("LOS", "Murtala Muhammed International Airport", "مطار مرتلا محمد الدولي", "Lagos", "لاغوس", "Nigeria", "نيجيريا", "NG"),
    ("ABV", "Nnamdi Azikiwe International Airport", "مطار نامدي أزيكيوي الدولي", "Abuja", "أبوجا", "Nigeria", "نيجيريا", "NG"),
    ("ACC", "Kotoka International Airport", "مطار كوتوكا الدولي", "Accra", "أكرا", "Ghana", "غانا", "GH"),
    ("MRU", "Sir Seewoosagur Ramgoolam International Airport", "مطار سير سيوساغور رامغولام الدولي", "Port Louis", "بورت لويس", "Mauritius", "موريشيوس", "MU"),
    ("SEZ", "Seychelles International Airport", "مطار سيشل الدولي", "Mahé", "ماهي", "Seychelles", "سيشل", "SC"),
    ("JIB", "Djibouti–Ambouli International Airport", "مطار جيبوتي الدولي", "Djibouti", "جيبوتي", "Djibouti", "جيبوتي", "DJ"),
    ("MGQ", "Aden Adde International Airport", "مطار عدن عدي الدولي", "Mogadishu", "مقديشو", "Somalia", "الصومال", "SO"),
    # ---- Americas ---------------------------------------------------------
    ("JFK", "John F. Kennedy International Airport", "مطار جون كينيدي الدولي", "New York", "نيويورك", "United States", "الولايات المتحدة", "US"),
    ("EWR", "Newark Liberty International Airport", "مطار نيوارك ليبرتي الدولي", "Newark", "نيوارك", "United States", "الولايات المتحدة", "US"),
    ("LAX", "Los Angeles International Airport", "مطار لوس أنجلوس الدولي", "Los Angeles", "لوس أنجلوس", "United States", "الولايات المتحدة", "US"),
    ("SFO", "San Francisco International Airport", "مطار سان فرانسيسكو الدولي", "San Francisco", "سان فرانسيسكو", "United States", "الولايات المتحدة", "US"),
    ("ORD", "O'Hare International Airport", "مطار أوهير الدولي", "Chicago", "شيكاغو", "United States", "الولايات المتحدة", "US"),
    ("IAD", "Washington Dulles International Airport", "مطار واشنطن دالاس الدولي", "Washington", "واشنطن", "United States", "الولايات المتحدة", "US"),
    ("MIA", "Miami International Airport", "مطار ميامي الدولي", "Miami", "ميامي", "United States", "الولايات المتحدة", "US"),
    ("BOS", "Boston Logan International Airport", "مطار بوسطن لوغان الدولي", "Boston", "بوسطن", "United States", "الولايات المتحدة", "US"),
    ("IAH", "George Bush Intercontinental Airport", "مطار جورج بوش الدولي", "Houston", "هيوستن", "United States", "الولايات المتحدة", "US"),
    ("YYZ", "Toronto Pearson International Airport", "مطار تورونتو بيرسون الدولي", "Toronto", "تورونتو", "Canada", "كندا", "CA"),
    ("YUL", "Montréal–Trudeau International Airport", "مطار مونتريال ترودو الدولي", "Montréal", "مونتريال", "Canada", "كندا", "CA"),
    ("YVR", "Vancouver International Airport", "مطار فانكوفر الدولي", "Vancouver", "فانكوفر", "Canada", "كندا", "CA"),
    ("GRU", "São Paulo/Guarulhos International Airport", "مطار ساو باولو غوارولوس الدولي", "São Paulo", "ساو باولو", "Brazil", "البرازيل", "BR"),
    ("EZE", "Ministro Pistarini International Airport", "مطار وزير بيستاريني الدولي", "Buenos Aires", "بوينس آيرس", "Argentina", "الأرجنتين", "AR"),
    ("MEX", "Mexico City International Airport", "مطار مكسيكو سيتي الدولي", "Mexico City", "مكسيكو سيتي", "Mexico", "المكسيك", "MX"),
    # ---- Oceania ----------------------------------------------------------
    ("SYD", "Sydney Kingsford Smith Airport", "مطار سيدني", "Sydney", "سيدني", "Australia", "أستراليا", "AU"),
    ("MEL", "Melbourne Airport", "مطار ملبورن", "Melbourne", "ملبورن", "Australia", "أستراليا", "AU"),
    ("BNE", "Brisbane Airport", "مطار بريزبن", "Brisbane", "بريزبن", "Australia", "أستراليا", "AU"),
    ("PER", "Perth Airport", "مطار بيرث", "Perth", "بيرث", "Australia", "أستراليا", "AU"),
    ("AKL", "Auckland Airport", "مطار أوكلاند", "Auckland", "أوكلاند", "New Zealand", "نيوزيلندا", "NZ"),
)
# fmt: on


def sync(airport_model) -> tuple[int, int]:
    """Upsert the catalogue, keyed on IATA code.

    Takes the model class as an argument so a migration can hand in its
    historical version. Idempotent: re-running refreshes names and leaves any
    `is_active` an agent has changed alone, because switching an airport off is
    an editorial decision and a re-seed has no business overriding it.

    Returns (created, updated).
    """
    created = updated = 0
    for order, row in enumerate(AIRPORTS):
        iata, name_en, name_ar, city_en, city_ar, country_en, country_ar, cc = row
        _, was_created = airport_model.objects.update_or_create(
            iata_code=iata,
            defaults={
                "name_en": name_en,
                "name_ar": name_ar,
                "city_en": city_en,
                "city_ar": city_ar,
                "country_en": country_en,
                "country_ar": country_ar,
                "country_code": cc,
                "is_popular": iata in POPULAR,
                "order": POPULAR.index(iata) if iata in POPULAR else order + 100,
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return created, updated

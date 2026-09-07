from django.core.management.base import BaseCommand

from apps.inquiries.models import InquiryField

# What the website asks once a service is chosen, on top of the name, email,
# phone and message it always asks.
#
# These rows are the forms. The contact page and the service pages both render
# them — /flights and the contact form's Flight questions are one definition,
# not two that drift. They started life as a table in the frontend's source;
# moving them here is what lets an agent change a question without a deploy.
#
# The labels are the ones those forms already carried, in both languages.
#
# Each row: key, label_ar, label_en, type, and whatever that type needs.
FIELDS = {
    "FLIGHT": [
        {
            "key": "trip_type",
            "label_ar": "نوع الرحلة",
            "label_en": "Trip type",
            "field_type": "SEGMENTED",
            "is_required": True,
            "options_ar": "ذهاب وعودة\nذهاب فقط",
            "options_en": "Round trip\nOne way",
        },
        {
            "key": "cabin_class",
            "label_ar": "درجة السفر",
            "label_en": "Cabin class",
            "field_type": "SELECT",
            "options_ar": "الدرجة السياحية\nالسياحية المميزة\nدرجة رجال الأعمال\nالدرجة الأولى",
            "options_en": "Economy\nPremium economy\nBusiness\nFirst",
        },
        {
            "key": "from",
            "label_ar": "من",
            "label_en": "From",
            "field_type": "AIRPORT",
            "is_required": True,
        },
        {
            "key": "to",
            "label_ar": "إلى",
            "label_en": "To",
            "field_type": "AIRPORT",
            "is_required": True,
        },
        {
            "key": "depart",
            "label_ar": "تاريخ المغادرة",
            "label_en": "Departure date",
            "field_type": "DATE",
            "is_required": True,
            "not_past": True,
        },
        {
            "key": "return",
            "label_ar": "تاريخ العودة",
            "label_en": "Return date",
            "field_type": "DATE",
            "not_past": True,
            "not_before": "depart",
            # Only on a round trip: a one-way has no return to ask about.
            # Matched against the English option, so the rule holds whichever
            # language the visitor is reading in.
            "show_when_key": "trip_type",
            "show_when_value": "Round trip",
        },
        {
            "key": "passengers",
            "label_ar": "عدد المسافرين",
            "label_en": "Passengers",
            "field_type": "STEPPER",
            "min_value": 1,
            "max_value": 9,
        },
    ],
    "HOTEL": [
        {
            "key": "city",
            "label_ar": "المدينة أو الوجهة",
            "label_en": "City or destination",
            "field_type": "CITY",
            "is_required": True,
            "placeholder_ar": "مثال: دبي",
            "placeholder_en": "e.g. Dubai",
        },
        {
            "key": "stars",
            "label_ar": "تصنيف الفندق",
            "label_en": "Hotel rating",
            "field_type": "SEGMENTED",
            "options_ar": "أي تصنيف\n5\n4\n3",
            "options_en": "Any rating\n5\n4\n3",
        },
        {
            "key": "check_in",
            "label_ar": "تاريخ الوصول",
            "label_en": "Check-in",
            "field_type": "DATE",
            "is_required": True,
            "not_past": True,
        },
        {
            "key": "check_out",
            "label_ar": "تاريخ المغادرة",
            "label_en": "Check-out",
            "field_type": "DATE",
            "is_required": True,
            "not_past": True,
            "not_before": "check_in",
        },
        {
            "key": "rooms",
            "label_ar": "عدد الغرف",
            "label_en": "Rooms",
            "field_type": "STEPPER",
            "min_value": 1,
            "max_value": 6,
        },
        {
            "key": "guests",
            "label_ar": "عدد الضيوف",
            "label_en": "Guests",
            "field_type": "STEPPER",
            "min_value": 1,
            "max_value": 9,
        },
    ],
    "VISA": [
        {
            "key": "travellers",
            "label_ar": "عدد المتقدمين",
            "label_en": "Applicants",
            "field_type": "STEPPER",
            "min_value": 1,
            "max_value": 9,
        },
        {
            "key": "travel_date",
            "label_ar": "تاريخ السفر المتوقع",
            "label_en": "Expected travel date",
            "field_type": "DATE",
            "not_past": True,
        },
    ],
    "CRUISE": [
        {
            "key": "departure_port",
            "label_ar": "ميناء المغادرة",
            "label_en": "Departure port",
            "field_type": "TEXT",
            "is_required": True,
        },
        {
            "key": "sail_date",
            "label_ar": "تاريخ الإبحار",
            "label_en": "Sailing date",
            "field_type": "DATE",
            "not_past": True,
        },
        {
            "key": "nights",
            "label_ar": "عدد الليالي",
            "label_en": "Nights",
            "field_type": "STEPPER",
            "min_value": 2,
            "max_value": 21,
        },
        {
            "key": "travellers",
            "label_ar": "عدد المسافرين",
            "label_en": "Travellers",
            "field_type": "STEPPER",
            "min_value": 1,
            "max_value": 9,
        },
        {
            "key": "cabin_type",
            "label_ar": "نوع الكابينة",
            "label_en": "Cabin",
            "field_type": "SELECT",
            "options_ar": "أي كابينة\nداخلية\nبإطلالة بحرية\nبشرفة\nجناح",
            "options_en": "Any cabin\nInside\nOcean view\nBalcony\nSuite",
        },
    ],
    # The trip planner: for travellers whose trip is not one of the ready-made
    # packages. It asks only what an agent needs to price a custom itinerary.
    "PACKAGE": [
        {
            "key": "destination",
            "label_ar": "الوجهة",
            "label_en": "Destination",
            "field_type": "CITY",
            "is_required": True,
            "placeholder_ar": "مثال: جورجيا، ماليزيا، أو أكثر من وجهة",
            "placeholder_en": "e.g. Georgia, Malaysia, or several places",
            "group_ar": "الوجهة والتواريخ",
            "group_en": "Destination and dates",
        },
        {
            "key": "travel_date",
            "label_ar": "تاريخ السفر المتوقع",
            "label_en": "Expected travel date",
            "field_type": "DATE",
            "not_past": True,
            "group_ar": "الوجهة والتواريخ",
            "group_en": "Destination and dates",
        },
        {
            "key": "nights",
            "label_ar": "عدد الليالي",
            "label_en": "Nights",
            "field_type": "STEPPER",
            "min_value": 1,
            "max_value": 21,
            "group_ar": "الوجهة والتواريخ",
            "group_en": "Destination and dates",
        },
        {
            "key": "travellers",
            "label_ar": "عدد المسافرين",
            "label_en": "Travellers",
            "field_type": "STEPPER",
            "min_value": 1,
            "max_value": 12,
            "group_ar": "الوجهة والتواريخ",
            "group_en": "Destination and dates",
        },
        {
            "key": "hotel_level",
            "label_ar": "مستوى الفندق",
            "label_en": "Hotel level",
            "field_type": "SEGMENTED",
            "options_ar": "أي مستوى\n5 نجوم\n4 نجوم\n3 نجوم",
            "options_en": "Any level\n5 stars\n4 stars\n3 stars",
            "group_ar": "أسلوب السفر",
            "group_en": "Travel style",
        },
        {
            "key": "budget",
            "label_ar": "الميزانية التقريبية للفرد",
            "label_en": "Approximate budget per person",
            "field_type": "SELECT",
            "options_ar": "أي ميزانية\nأقل من 5,000 ر.س\n5,000 – 10,000 ر.س\n10,000 – 20,000 ر.س\nأكثر من 20,000 ر.س",
            "options_en": "Any budget\nUnder SAR 5,000\nSAR 5,000 – 10,000\nSAR 10,000 – 20,000\nOver SAR 20,000",
            "group_ar": "أسلوب السفر",
            "group_en": "Travel style",
        },
        {
            "key": "services",
            "label_ar": "الخدمات التي تريد تضمينها",
            "label_en": "What should we include?",
            "field_type": "CHECKBOX",
            "is_wide": True,
            "options_ar": "تذاكر الطيران\nالإقامة\nالتنقلات\nالجولات السياحية\nالتأشيرة\nتأمين السفر\nالوجبات",
            "options_en": "Flights\nAccommodation\nTransfers\nGuided tours\nVisa\nTravel insurance\nMeals",
            "group_ar": "الخدمات المطلوبة",
            "group_en": "What to include",
        },
    ],
    "CORPORATE": [
        {
            "key": "company",
            "label_ar": "اسم الشركة",
            "label_en": "Company name",
            "field_type": "TEXT",
            "is_required": True,
        },
        {
            "key": "travellers",
            "label_ar": "عدد الموظفين المسافرين",
            "label_en": "Travelling staff",
            "field_type": "STEPPER",
            "min_value": 1,
            "max_value": 99,
        },
        {
            "key": "trip_frequency",
            "label_ar": "عدد الرحلات المتوقعة سنويًا",
            "label_en": "Trips per year",
            "field_type": "NUMBER",
        },
    ],
}


class Command(BaseCommand):
    help = "Load the website's per-service form questions. Safe to re-run."

    def handle(self, *args, **options):
        created = updated = 0

        for service_type, rows in FIELDS.items():
            for order, spec in enumerate(rows):
                defaults = {
                    "label_ar": spec["label_ar"],
                    "label_en": spec["label_en"],
                    "field_type": spec.get("field_type", "TEXT"),
                    "placeholder_ar": spec.get("placeholder_ar", ""),
                    "placeholder_en": spec.get("placeholder_en", ""),
                    "options_ar": spec.get("options_ar", ""),
                    "options_en": spec.get("options_en", ""),
                    "is_required": spec.get("is_required", False),
                    "min_value": spec.get("min_value"),
                    "max_value": spec.get("max_value"),
                    "not_past": spec.get("not_past", False),
                    "not_before": spec.get("not_before", ""),
                    "show_when_key": spec.get("show_when_key", ""),
                    "show_when_value": spec.get("show_when_value", ""),
                    "is_wide": spec.get("is_wide", False),
                    "group_ar": spec.get("group_ar", ""),
                    "group_en": spec.get("group_en", ""),
                    "order": order,
                    "is_active": True,
                }
                _, was_created = InquiryField.objects.update_or_create(
                    service_type=service_type, key=spec["key"], defaults=defaults
                )
                created += int(was_created)
                updated += int(not was_created)

        # Rows for a service this table no longer describes would keep being
        # asked with nothing here to explain them.
        wanted = {(service, row["key"]) for service, rows in FIELDS.items() for row in rows}
        stale = [
            field
            for field in InquiryField.objects.all()
            if (field.service_type, field.key) not in wanted
        ]
        if stale:
            self.stdout.write(
                self.style.WARNING(
                    "Leaving questions added in the panel alone: "
                    + ", ".join(f"{f.service_type}.{f.key}" for f in stale)
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"Form questions: {created} created, {updated} refreshed.")
        )
        self.stdout.write(
            "Edit them in the panel under Contact form questions — the website asks whatever is there."
        )

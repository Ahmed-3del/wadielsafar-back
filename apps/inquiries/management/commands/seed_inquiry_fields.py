from django.core.management.base import BaseCommand

from apps.inquiries.models import InquiryField

# The questions the contact form asks once a service is chosen, on top of the
# name, email, phone and message it always asks.
#
# These are a starting point, not a fixture: the whole reason the rows exist is
# that an agent can change what is asked without a deployment. Matched on
# (service, key), so re-running updates in place and leaves anything an editor
# added alone.
#
# key, label_ar, label_en, type, required, options_ar, options_en
FIELDS = {
    "FLIGHT": [
        ("from", "من", "From", "TEXT", True, "", ""),
        ("to", "إلى", "To", "TEXT", True, "", ""),
        ("depart", "تاريخ المغادرة", "Departure date", "DATE", True, "", ""),
        ("return", "تاريخ العودة", "Return date", "DATE", False, "", ""),
        ("passengers", "عدد المسافرين", "Passengers", "NUMBER", False, "", ""),
        (
            "cabin_class",
            "درجة السفر",
            "Cabin class",
            "SELECT",
            False,
            "الدرجة السياحية\nرجال الأعمال\nالأولى",
            "Economy\nBusiness\nFirst",
        ),
    ],
    "HOTEL": [
        ("city", "المدينة", "City", "TEXT", True, "", ""),
        ("check_in", "تاريخ الوصول", "Check-in", "DATE", True, "", ""),
        ("check_out", "تاريخ المغادرة", "Check-out", "DATE", True, "", ""),
        ("rooms", "عدد الغرف", "Rooms", "NUMBER", False, "", ""),
        ("guests", "عدد النزلاء", "Guests", "NUMBER", False, "", ""),
        (
            "stars",
            "تصنيف الفندق",
            "Hotel rating",
            "SELECT",
            False,
            "5 نجوم\n4 نجوم\n3 نجوم",
            "5 stars\n4 stars\n3 stars",
        ),
    ],
    "PACKAGE": [
        ("nights", "عدد الليالي", "Nights", "NUMBER", False, "", ""),
        ("travellers", "عدد المسافرين", "Travellers", "NUMBER", False, "", ""),
        (
            "budget",
            "الميزانية للفرد",
            "Budget per person",
            "SELECT",
            False,
            "أقل من 5,000 ر.س\n5,000 – 10,000 ر.س\n10,000 – 20,000 ر.س\nأكثر من 20,000 ر.س",
            "Under SAR 5,000\nSAR 5,000 – 10,000\nSAR 10,000 – 20,000\nOver SAR 20,000",
        ),
    ],
    "VISA": [
        ("visa_country", "الدولة", "Country", "TEXT", True, "", ""),
        (
            "purpose",
            "الغرض من السفر",
            "Purpose of travel",
            "SELECT",
            False,
            "سياحة\nعمل\nدراسة\nعمرة",
            "Tourism\nBusiness\nStudy\nUmrah",
        ),
        ("travellers", "عدد المتقدمين", "Applicants", "NUMBER", False, "", ""),
    ],
    "CRUISE": [
        ("departure_port", "ميناء المغادرة", "Departure port", "TEXT", False, "", ""),
        ("sail_date", "تاريخ الإبحار", "Sailing date", "DATE", False, "", ""),
        ("nights", "عدد الليالي", "Nights", "NUMBER", False, "", ""),
        (
            "cabin_type",
            "نوع الكابينة",
            "Cabin",
            "SELECT",
            False,
            "داخلية\nبإطلالة بحرية\nبشرفة\nجناح",
            "Inside\nOcean view\nBalcony\nSuite",
        ),
    ],
    "CORPORATE": [
        ("company", "اسم الشركة", "Company name", "TEXT", True, "", ""),
        ("travellers", "عدد الموظفين المسافرين", "Travelling staff", "NUMBER", False, "", ""),
        ("trip_frequency", "عدد الرحلات المتوقعة سنويًا", "Trips per year", "NUMBER", False, "", ""),
    ],
}


class Command(BaseCommand):
    help = "Load the contact form's per-service questions. Safe to re-run."

    def handle(self, *args, **options):
        created = updated = 0
        for service_type, rows in FIELDS.items():
            for order, (key, label_ar, label_en, field_type, required, opt_ar, opt_en) in enumerate(
                rows
            ):
                _, was_created = InquiryField.objects.update_or_create(
                    service_type=service_type,
                    key=key,
                    defaults={
                        "label_ar": label_ar,
                        "label_en": label_en,
                        "field_type": field_type,
                        "is_required": required,
                        "options_ar": opt_ar,
                        "options_en": opt_en,
                        "order": order,
                        "is_active": True,
                    },
                )
                created += int(was_created)
                updated += int(not was_created)

        self.stdout.write(
            self.style.SUCCESS(f"Contact form questions: {created} created, {updated} refreshed.")
        )
        self.stdout.write(
            "Edit them in the panel under Contact form fields — the website asks whatever is there."
        )

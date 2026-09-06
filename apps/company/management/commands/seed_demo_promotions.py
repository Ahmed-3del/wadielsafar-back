from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.company.models import Promotion, PromotionIconChoices
from common.utilities import guard_demo_write

# The three "ways to save" cards, in the client's own words.
#
# The figures — 15%, 10%, thirty days — come from the homepage feedback and are
# reproduced verbatim. Nothing here is a number this project invented, and any
# of it can be edited or switched off from the panel without a deployment.
PROMOTIONS = [
    {
        "title_ar": "خصم العميل الجديد",
        "title_en": "New customer discount",
        # Deliberately not the sticky bar's sentence word for word: the two
        # carry the same offer and appear on the same screen.
        "description_ar": "اذكر الكود عند الحجز واحصل على الخصم مباشرة على أول رحلة تحجزها معنا.",
        "description_en": "Quote the code when you book and the discount comes off your first trip with us.",
        "badge_ar": "15%",
        "badge_en": "15%",
        "code": "WELCOME15",
        "icon": PromotionIconChoices.TAG,
        "link": "",
        # No announced end date: the card shows the offer without a timer.
        "days_from_now": None,
    },
    {
        "title_ar": "عرض الحجز المبكر",
        "title_en": "Early bird offer",
        "description_ar": "احجز قبل موعد سفرك بـ 30 يوماً أو أكثر واحصل على السعر المبكر.",
        "description_en": "Book 30 days or more before you travel and pay the early price.",
        # No badge: the countdown below it is this card's headline figure, and
        # a static "30 days" beside a ticking clock reads as a contradiction.
        "badge_ar": "",
        "badge_en": "",
        "code": "",
        "icon": PromotionIconChoices.CLOCK,
        # This one has a page of its own to send people to; the other two are
        # applied by an agent, so they lead to the contact form with the code.
        "link": "/packages",
        # Demo only — see the warning printed at the end of this command.
        "days_from_now": 14,
    },
    {
        "title_ar": "برنامج الترشيح",
        "title_en": "Referral programme",
        "description_ar": "رشّح صديقاً واحصلا معاً على خصم 10% على الحجز التالي.",
        "description_en": "Refer a friend and you both get 10% off your next booking.",
        "badge_ar": "10%",
        "badge_en": "10%",
        "code": "",
        "icon": PromotionIconChoices.GIFT,
        "link": "",
        "days_from_now": None,
    },
]


class Command(BaseCommand):
    help = "Seed the homepage 'ways to save' cards."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, **options):
        # These cards carry live discounts and a public deadline, so overwriting
        # them outside development takes the same deliberate flag as the rest.
        guard_demo_write(options["force"])

        now = timezone.now()
        written = 0

        for order, spec in enumerate(PROMOTIONS):
            # Copied, not popped: popping would empty the module-level list on
            # the second call in a process, and seed_demo runs in-process.
            fields = {key: value for key, value in spec.items() if key != "days_from_now"}
            days = spec["days_from_now"]
            # The end of that day in Riyadh, so the countdown lands on a round
            # moment rather than on whatever second the seeder ran. Localised
            # first: replacing the hour on a UTC instant would set the deadline
            # to two in the morning local time.
            ends_at = (
                timezone.localtime(now + timedelta(days=days)).replace(
                    hour=23, minute=59, second=0, microsecond=0
                )
                if days is not None
                else None
            )
            Promotion.objects.update_or_create(
                title_en=fields["title_en"],
                defaults={**fields, "ends_at": ends_at, "order": order, "is_active": True},
            )
            written += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {written} promotions."))
        self.stdout.write(
            self.style.WARNING(
                "The early-bird end date is demo data, two weeks out. Set the real "
                "deadline on the promotion in the panel before launch — the homepage "
                "counts down to it in public."
            )
        )

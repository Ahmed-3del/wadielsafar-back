from django.db.models import Count, Q
from django.utils import timezone

from apps.destinations.models import Destination
from apps.flights.models import FlightDeal
from apps.hotels.models import Hotel
from apps.inquiries.models import Inquiry
from apps.offers.models import Offer
from apps.packages.models import Package
from apps.testimonials.models import Testimonial
from apps.visas.models import VisaType
from common.constants import InquiryStatusChoices

RECENT_INQUIRY_LIMIT = 5


class DashboardService:
    @staticmethod
    def get_stats() -> dict:
        testimonials = Testimonial.objects.aggregate(
            published=Count("id", filter=Q(is_approved=True, is_visible=True)),
            pending_approval=Count("id", filter=Q(is_approved=False)),
        )
        return {
            "inquiries": DashboardService._inquiry_stats(),
            "content": {
                "destinations": Destination.objects.filter(is_active=True).count(),
                "packages": Package.objects.filter(is_active=True).count(),
                "hotels": Hotel.objects.filter(is_active=True).count(),
                "flights": FlightDeal.objects.filter(is_active=True).count(),
                "visas": VisaType.objects.filter(is_active=True).count(),
                "offers": Offer.objects.filter(is_active=True).count(),
                "testimonials": testimonials["published"],
            },
            "testimonials": {"pending_approval": testimonials["pending_approval"]},
        }

    @staticmethod
    def _inquiry_stats() -> dict:
        # One conditional-aggregate query for every status at once, rather
        # than a count query per status.
        per_status = {
            f"status_{choice.value}": Count("id", filter=Q(status=choice.value))
            for choice in InquiryStatusChoices
        }
        counts = Inquiry.objects.aggregate(total=Count("id"), **per_status)
        by_status = {
            choice.value: counts[f"status_{choice.value}"] for choice in InquiryStatusChoices
        }
        recent = list(
            Inquiry.objects.order_by("-created_at").values(
                "id", "name", "service_type", "status", "created_at"
            )[:RECENT_INQUIRY_LIMIT]
        )
        for row in recent:
            # `.values()` bypasses the serializer layer, so localize here to
            # match the +03:00 timestamps every other endpoint renders.
            row["created_at"] = timezone.localtime(row["created_at"])
        return {
            "total": counts["total"],
            "new": by_status[InquiryStatusChoices.NEW.value],
            "by_status": by_status,
            "recent": recent,
        }

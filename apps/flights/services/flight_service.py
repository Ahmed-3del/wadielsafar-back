from apps.flights.models import FlightDeal


class FlightService:
    @staticmethod
    def get_featured(limit=6):
        return FlightDeal.objects.filter(is_active=True, is_featured=True).order_by("price_from")[
            :limit
        ]

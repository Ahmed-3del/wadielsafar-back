from apps.cruises.models import Cruise


class CruiseService:
    @staticmethod
    def get_featured(limit=6):
        return (
            Cruise.objects.filter(is_active=True, is_featured=True)
            .select_related("destination")
            .order_by("price_from")[:limit]
        )

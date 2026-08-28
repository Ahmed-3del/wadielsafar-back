from apps.hotels.models import Hotel


class HotelService:
    @staticmethod
    def get_featured(limit=6):
        return (
            Hotel.objects.filter(is_active=True, is_featured=True)
            .select_related("destination")
            .prefetch_related("amenities")
            .order_by("-star_rating", "name_en")[:limit]
        )

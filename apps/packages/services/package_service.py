from apps.packages.models import Package


class PackageService:
    @staticmethod
    def get_featured(limit=6):
        return Package.objects.filter(is_active=True, is_featured=True).order_by("-created_at")[
            :limit
        ]

    @staticmethod
    def compute_duration_days(package):
        """Derives duration from the itinerary day count rather than trusting
        the editable `duration_days` field, which can drift once itinerary
        days are added/removed after the package was first created."""
        day_count = package.itinerary.count()
        if day_count == 0:
            return package.duration_days
        package.duration_days = day_count
        package.save(update_fields=["duration_days"])
        return package.duration_days

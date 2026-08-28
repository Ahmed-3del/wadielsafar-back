from django.core.management.base import BaseCommand

from apps.airports.data.catalogue import sync
from apps.airports.models import Airport


class Command(BaseCommand):
    help = "Load or refresh the shipped airport catalogue. Safe to re-run."

    def handle(self, *args, **options):
        created, updated = sync(Airport)
        self.stdout.write(self.style.SUCCESS(f"Airports: {created} created, {updated} refreshed."))

from django.core.management.base import BaseCommand

from apps.cruises.data.catalogue import sync
from apps.cruises.models import CruisePort


class Command(BaseCommand):
    help = "Load or refresh the shipped cruise-port catalogue. Safe to re-run."

    def handle(self, *args, **options):
        created, updated = sync(CruisePort)
        self.stdout.write(self.style.SUCCESS(f"Cruise ports: {created} created, {updated} refreshed."))

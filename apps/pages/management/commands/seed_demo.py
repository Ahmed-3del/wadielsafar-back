"""Fill an empty database with enough content to use the site.

Runs every `seed_demo_*` command in dependency order. It lives in `pages`
because that app already owns what the site shows — the homepage's running
order is next door.

Demonstration content, not the company's catalogue. Every row it writes is
editable in the panel and is meant to be replaced.

Three things it deliberately does not touch:

  Partners      — logos imply a commercial relationship, and inventing one is
                  a claim the site cannot support.
  Testimonials  — the same, for customer quotes.
  Certificates  — the real licences are already loaded; a fake one is worse
                  than none.

Reference data (airports, navigation, branches, social links, the homepage
running order) ships in migrations rather than here, so it is present on any
database that has been migrated.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.pages.models import HomeSection

# Order matters: hotels, packages and cruises all point at a destination.
SEEDERS = [
    "seed_demo_destinations",
    "seed_demo_hotels",
    "seed_demo_packages",
    "seed_demo_flights",
    "seed_demo_cruises",
    "seed_demo_visas",
    "seed_demo_offers",
    # Reference data, not demo content — safe to re-run and needed for the
    # departure and arrival pickers to have anything in them.
    "seed_airports",
]


class Command(BaseCommand):
    help = "Load the whole demo dataset. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run even when DEBUG is off. This overwrites content, so be sure.",
        )

    def handle(self, *args, **options):
        for name in SEEDERS:
            self.stdout.write(self.style.HTTP_INFO(f"→ {name}"))
            # seed_airports is reference data and takes no --force flag.
            if name == "seed_airports":
                call_command(name)
            else:
                call_command(name, force=options["force"])

        # The cruises section ships switched off because the database ships
        # with one cruise, and a rail holding one card is mostly empty track.
        # Once this command has filled it, that reason is gone.
        switched_on = HomeSection.objects.filter(key="CRUISES", is_active=False).update(
            is_active=True
        )
        if switched_on:
            self.stdout.write("Homepage: cruises section switched on now it has content.")

        self.stdout.write(self.style.SUCCESS("\nDemo dataset loaded."))

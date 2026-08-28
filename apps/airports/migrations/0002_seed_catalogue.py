from django.db import migrations

from apps.airports.data.catalogue import sync


def load_catalogue(apps, schema_editor):
    """Ship the airport list with the schema.

    The catalogue is reference data — airports that exist, nothing about what
    the company sells — so it belongs in the migration rather than in a demo
    fixture an operator has to remember to run. `sync` is keyed on IATA code
    and idempotent, so `seed_airports` can refresh it later without conflict.
    """
    sync(apps.get_model("airports", "Airport"))


def unload_catalogue(apps, schema_editor):
    """Only remove what this migration put there.

    Matching on the shipped codes rather than truncating the table: an agent
    may have added airports of their own by the time anyone rolls back.
    """
    from apps.airports.data.catalogue import AIRPORTS

    apps.get_model("airports", "Airport").objects.filter(
        iata_code__in=[row[0] for row in AIRPORTS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("airports", "0001_initial")]

    operations = [migrations.RunPython(load_catalogue, unload_catalogue)]

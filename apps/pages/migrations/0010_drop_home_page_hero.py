from django.db import migrations, models


def drop(apps, schema_editor):
    """The homepage's full-height photo hero was replaced by the search band
    going first instead — see SearchBand's own comment on the frontend. An
    editor could still open "Home" here, change its background, save it, and
    see nothing change: this row had not been read by anything since. Deleted
    along with the choice, rather than left behind it, so it cannot be edited
    again under a page nothing renders it on.
    """
    PageHero = apps.get_model("pages", "PageHero")
    PageHero.objects.filter(page_key="home").delete()


def restore(apps, schema_editor):
    """Not a real restore — there is nothing this ever fed on the site to put
    back. Recreates an inactive placeholder only so the choice and a row for
    it exist together again if this migration is ever reversed."""
    PageHero = apps.get_model("pages", "PageHero")
    if PageHero.objects.filter(page_key="home").exists():
        return
    PageHero.objects.create(page_key="home", media_type="NONE", is_active=False)


class Migration(migrations.Migration):
    dependencies = [("pages", "0009_loyalty_home_section")]

    operations = [
        migrations.AlterField(
            model_name="pagehero",
            name="page_key",
            field=models.CharField(
                choices=[
                    ("destinations", "Destinations"),
                    ("packages", "Packages"),
                    ("visas", "Visas"),
                    ("flights", "Flights"),
                    ("hotels", "Hotels"),
                    ("cruises", "Cruises"),
                    ("offers", "Offers"),
                    ("corporate", "Corporate"),
                    ("about", "About"),
                    ("contact", "Contact"),
                ],
                max_length=32,
                unique=True,
            ),
        ),
        migrations.RunPython(drop, restore),
    ]

from django.db import migrations, models


def feature_what_the_homepage_already_shows(apps, schema_editor):
    """Before this field existed, the homepage rail was just the first 8 visas
    in the default (country, name) ordering — see VisaSection.tsx's own prior
    `.slice(0, 8)`. Marking exactly those as featured is what keeps the rail
    showing the same visas today as it did yesterday; an editor changes it
    from here on, not this migration.
    """
    VisaType = apps.get_model("visas", "VisaType")
    # Matches the model's own Meta.ordering = ("country", "name_en") exactly
    # — "country" there sorts by the foreign key's raw id, not the country's
    # name, so this does too.
    ids = list(
        VisaType.objects.order_by("country_id", "name_en").values_list("id", flat=True)[:8]
    )
    VisaType.objects.filter(id__in=ids).update(is_featured=True)


def unfeature(apps, schema_editor):
    """Symbolic only: is_featured itself is dropped by the reverse of the
    AddField below, taking every row's flag with it."""


class Migration(migrations.Migration):

    dependencies = [
        ("visas", "0006_visacountry_cover_image_visatype_cover_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="visatype",
            name="is_featured",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(feature_what_the_homepage_already_shows, unfeature),
    ]

from django.db import migrations, models
from django.db.models import F

# The loyalty banner used to be hard-coded directly under the search band,
# with no row here and nothing an editor could do about its place on the
# page — the same story as RECOMMENDATIONS in the migration before this one.
# Inserted at the very front, which is where it already renders, so nothing
# on the live site moves.
KEY = "LOYALTY"


def seed(apps, schema_editor):
    HomeSection = apps.get_model("pages", "HomeSection")
    if HomeSection.objects.filter(key=KEY).exists():
        return
    HomeSection.objects.filter(order__gte=0).update(order=F("order") + 1)
    HomeSection.objects.create(key=KEY, order=0, is_active=True)


def unseed(apps, schema_editor):
    HomeSection = apps.get_model("pages", "HomeSection")
    section = HomeSection.objects.filter(key=KEY).first()
    if section is None:
        return
    order = section.order
    section.delete()
    HomeSection.objects.filter(order__gt=order).update(order=F("order") - 1)


class Migration(migrations.Migration):
    dependencies = [("pages", "0008_hide_explorer_home_section")]

    operations = [
        migrations.AlterField(
            model_name="homesection",
            name="key",
            field=models.CharField(
                choices=[
                    ("RECOMMENDATIONS", "You might also like (search cross-sell)"),
                    ("LOYALTY", "Loyalty programme banner"),
                    ("SERVICES", "What we offer"),
                    ("SAVINGS", "Ways to save"),
                    ("EXPLORER", "Budget explorer"),
                    ("DESTINATIONS", "Popular destinations"),
                    ("PACKAGES", "Featured packages"),
                    ("OFFERS", "Offers"),
                    ("VISAS", "Visa services"),
                    ("CRUISES", "Cruises"),
                    ("TRUST", "Why travel with us"),
                    ("PARTNERS", "Partners"),
                    ("TESTIMONIALS", "Testimonials"),
                    ("CTA", "Closing call to action"),
                ],
                max_length=32,
                unique=True,
            ),
        ),
        migrations.RunPython(seed, unseed),
    ]

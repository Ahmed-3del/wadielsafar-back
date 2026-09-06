from django.db import migrations, models
from django.db.models import F


def drop(apps, schema_editor):
    """The branch cards moved into the footer, where they appear on every page.

    A section of them on the homepage as well was the same four addresses
    twice on one screen. The rows below it close the gap they leave, so an
    order an editor has arranged does not develop a hole.
    """
    HomeSection = apps.get_model("pages", "HomeSection")
    section = HomeSection.objects.filter(key="BRANCHES").first()
    if section is None:
        return

    order = section.order
    section.delete()
    HomeSection.objects.filter(order__gt=order).update(order=F("order") - 1)


def restore(apps, schema_editor):
    HomeSection = apps.get_model("pages", "HomeSection")
    if HomeSection.objects.filter(key="BRANCHES").exists():
        return
    last = HomeSection.objects.order_by("-order").first()
    HomeSection.objects.create(
        key="BRANCHES", order=(last.order + 1) if last else 0, is_active=True
    )


class Migration(migrations.Migration):
    dependencies = [("pages", "0005_home_sections_savings_branches")]

    operations = [
        migrations.AlterField(
            model_name="homesection",
            name="key",
            field=models.CharField(
                choices=[
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
        migrations.RunPython(drop, restore),
    ]

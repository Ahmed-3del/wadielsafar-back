from django.db import migrations, models
from django.db.models import F

# Two blocks the client's homepage feedback asked for.
#
# Both are inserted relative to the rows already in the table rather than at a
# fixed index: the order is an editor's to arrange, and a site that has been
# rearranged since launch must not have its running order rewritten by a
# deployment.
NEW = [
    # Directly under the add-on services, which is where the feedback puts it:
    # someone has just read what else we sell, and this is what it costs less.
    ("SAVINGS", "SERVICES", "after"),
    # Above the closing call to action: the last thing before "talk to us" is
    # where to walk in and do it.
    ("BRANCHES", "CTA", "before"),
]


def insert(HomeSection, key, anchor_key, position):
    if HomeSection.objects.filter(key=key).exists():
        return

    anchor = HomeSection.objects.filter(key=anchor_key).first()
    if anchor is None:
        last = HomeSection.objects.order_by("-order").first()
        order = (last.order + 1) if last else 0
    else:
        order = anchor.order + 1 if position == "after" else anchor.order

    HomeSection.objects.filter(order__gte=order).update(order=F("order") + 1)
    HomeSection.objects.create(key=key, order=order, is_active=True)


def seed(apps, schema_editor):
    HomeSection = apps.get_model("pages", "HomeSection")
    for key, anchor, position in NEW:
        insert(HomeSection, key, anchor, position)


def unseed(apps, schema_editor):
    apps.get_model("pages", "HomeSection").objects.filter(
        key__in=[key for key, _, _ in NEW]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("pages", "0004_seed_home_sections")]

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
                    ("BRANCHES", "Branch locations"),
                    ("TESTIMONIALS", "Testimonials"),
                    ("CTA", "Closing call to action"),
                ],
                max_length=32,
                unique=True,
            ),
        ),
        migrations.RunPython(seed, unseed),
    ]

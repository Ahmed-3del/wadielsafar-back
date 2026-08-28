from django.db import migrations

# The homepage as it ships. Order is the list order; the third value is whether
# the section starts switched on.
#
# Twelve sections were on by default and the page ran to 18 screens on a phone,
# which is several times further than anyone scrolls. The three switched off
# below are off for a reason an editor can undo in one click:
#
#   PACKAGES  — the budget explorer above it renders the same package cards, so
#               a visitor met the same five trips twice in a row.
#   CRUISES   — a carousel built for a rail, holding one cruise: ~700px of
#               empty track. Worth switching on once there is a rail's worth.
#   PARTNERS  — the shipped rows carry placeholder photography rather than
#               partner logos, which reads as unfinished. Worth switching on
#               once the real marks are uploaded.
SECTIONS = [
    ("SERVICES", True),
    ("EXPLORER", True),
    ("DESTINATIONS", True),
    ("OFFERS", True),
    ("VISAS", True),
    ("PACKAGES", False),
    ("CRUISES", False),
    ("TRUST", True),
    ("TESTIMONIALS", True),
    ("PARTNERS", False),
    ("CTA", True),
]


def seed(apps, schema_editor):
    HomeSection = apps.get_model("pages", "HomeSection")
    for order, (key, is_active) in enumerate(SECTIONS):
        HomeSection.objects.update_or_create(
            key=key, defaults={"order": order, "is_active": is_active}
        )


def unseed(apps, schema_editor):
    apps.get_model("pages", "HomeSection").objects.filter(
        key__in=[key for key, _ in SECTIONS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("pages", "0003_homesection")]

    operations = [migrations.RunPython(seed, unseed)]

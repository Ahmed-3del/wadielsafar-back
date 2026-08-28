from django.db import migrations

# The navigation the site shipped with, moved from a hard-coded list in the
# front end into rows an editor can reorder. Seeded rather than left empty
# because a site with no navigation is broken, and because the point of this
# table is to be edited, not authored from scratch.
PRIMARY = [
    ("الرئيسية", "Home", "/"),
    ("الوجهات", "Destinations", "/destinations"),
    ("الباقات السياحية", "Packages", "/packages"),
    ("التأشيرات", "Visas", "/visas"),
    ("الطيران", "Flights", "/flights"),
    ("الفنادق", "Hotels", "/hotels"),
    ("الرحلات البحرية", "Cruises", "/cruises"),
    ("الشركات", "Corporate", "/corporate"),
]

SECONDARY = [
    ("العروض", "Offers", "/offers"),
    ("من نحن", "About Us", "/about"),
    ("تواصل معنا", "Contact Us", "/contact"),
]


def seed(apps, schema_editor):
    NavItem = apps.get_model("navigation", "NavItem")
    # Only on an empty table: re-running must never resurrect a link someone
    # deliberately deleted.
    if NavItem.objects.exists():
        return

    rows = [(g, i, r) for g, group in (("PRIMARY", PRIMARY), ("SECONDARY", SECONDARY))
            for i, r in enumerate(group, start=1)]
    NavItem.objects.bulk_create(
        NavItem(
            label_ar=label_ar,
            label_en=label_en,
            href=href,
            group=group,
            order=order,
            is_active=True,
        )
        for group, order, (label_ar, label_en, href) in rows
    )


def unseed(apps, schema_editor):
    NavItem = apps.get_model("navigation", "NavItem")
    hrefs = [r[2] for r in PRIMARY + SECONDARY]
    NavItem.objects.filter(href__in=hrefs).delete()


class Migration(migrations.Migration):
    dependencies = [("navigation", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]

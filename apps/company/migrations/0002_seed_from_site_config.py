from django.db import migrations

# Lifted verbatim from the frontend's src/config/site.ts, which is where these
# lived before the panel could edit them. Nothing new is asserted here: the
# numbers and profiles were already published on the site, they just could not
# be changed without a deploy.
BRANCHES = [
    ("الفرع الرئيسي", "Main branch", "+966115602558", "+966 11 560 2558"),
    ("فرع 1", "Branch 1", "+966112266745", "+966 11 226 6745"),
    ("فرع 2", "Branch 2", "+966112311372", "+966 11 231 1372"),
    ("فرع 3", "Branch 3", "+966112022107", "+966 11 202 2107"),
]

SOCIAL_LINKS = [
    ("FACEBOOK", "https://facebook.com/wadialsafartravel"),
    ("X", "https://x.com/wadialsafar"),
    ("INSTAGRAM", "https://instagram.com/wadialsafar_sa"),
    ("TIKTOK", "https://tiktok.com/@wadialsafar_sa"),
    ("SNAPCHAT", "https://snapchat.com/add/wadialsafar1"),
]


def seed(apps, schema_editor):
    Branch = apps.get_model("company", "Branch")
    SocialLink = apps.get_model("company", "SocialLink")

    for order, (name_ar, name_en, phone, display) in enumerate(BRANCHES):
        Branch.objects.update_or_create(
            phone=phone,
            defaults={
                "name_ar": name_ar,
                "name_en": name_en,
                "phone_display": display,
                "order": order,
            },
        )

    for order, (platform, url) in enumerate(SOCIAL_LINKS):
        SocialLink.objects.update_or_create(
            platform=platform, defaults={"url": url, "order": order}
        )


def unseed(apps, schema_editor):
    """Remove only what this migration added, in case an agent has since added
    branches or profiles of their own."""
    apps.get_model("company", "Branch").objects.filter(
        phone__in=[row[2] for row in BRANCHES]
    ).delete()
    apps.get_model("company", "SocialLink").objects.filter(
        platform__in=[row[0] for row in SOCIAL_LINKS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("company", "0001_initial")]

    operations = [migrations.RunPython(seed, unseed)]

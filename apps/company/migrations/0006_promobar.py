import common.validators.paths
from django.db import migrations, models

# Lifted verbatim from the frontend's messages/{ar,en}.json "Promo" namespace,
# which is where this lived before the panel could edit it. Nothing new is
# asserted here: this wording was already published on the site, it just
# could not be changed without a deploy.
HEADLINE_AR = "خصم 15% لعملاء وادي السفر الجدد على أول حجز"
HEADLINE_EN = "15% off for new Wadi Al Safar customers on your first booking"
CODE = "WELCOME15"
CTA_LABEL_AR = "احجز الآن"
CTA_LABEL_EN = "Book now"


def seed(apps, schema_editor):
    PromoBar = apps.get_model("company", "PromoBar")
    if PromoBar.objects.exists():
        return
    PromoBar.objects.create(
        headline_ar=HEADLINE_AR,
        headline_en=HEADLINE_EN,
        code=CODE,
        cta_label_ar=CTA_LABEL_AR,
        cta_label_en=CTA_LABEL_EN,
        link="/contact",
        is_active=True,
    )


def unseed(apps, schema_editor):
    """Not a real reverse — there is nowhere left for this to go back to once
    the panel may have changed it. Removes only the exact row this migration
    added, in case an agent has since edited it or added their own."""
    apps.get_model("company", "PromoBar").objects.filter(
        headline_en=HEADLINE_EN, code=CODE
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0005_promotion_cta_label_ar_promotion_cta_label_en_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PromoBar",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("headline_ar", models.CharField(max_length=200)),
                ("headline_en", models.CharField(max_length=200)),
                ("code", models.CharField(blank=True, max_length=32)),
                ("cta_label_ar", models.CharField(max_length=60)),
                ("cta_label_en", models.CharField(max_length=60)),
                (
                    "link",
                    models.CharField(
                        blank=True,
                        default="/contact",
                        max_length=200,
                        validators=[common.validators.paths.validate_internal_path],
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "promo bar",
                "verbose_name_plural": "promo bar",
            },
        ),
        migrations.RunPython(seed, unseed),
    ]

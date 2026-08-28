from django.db import migrations, models

# Country names are facts, not copy, so translating the ones we recognise is
# safe to do automatically. Anything not listed keeps its English spelling in
# both columns — the status quo, visible in the panel, and correctable by an
# editor. Nothing is guessed and nothing is lost.
COUNTRY_AR = {
    "saudi arabia": "السعودية",
    "united arab emirates": "الإمارات العربية المتحدة",
    "uae": "الإمارات العربية المتحدة",
    "kuwait": "الكويت",
    "qatar": "قطر",
    "bahrain": "البحرين",
    "oman": "عُمان",
    "egypt": "مصر",
    "jordan": "الأردن",
    "lebanon": "لبنان",
    "morocco": "المغرب",
    "tunisia": "تونس",
    "turkey": "تركيا",
    "türkiye": "تركيا",
    "georgia": "جورجيا",
    "azerbaijan": "أذربيجان",
    "armenia": "أرمينيا",
    "maldives": "المالديف",
    "sri lanka": "سريلانكا",
    "malaysia": "ماليزيا",
    "indonesia": "إندونيسيا",
    "thailand": "تايلاند",
    "singapore": "سنغافورة",
    "japan": "اليابان",
    "china": "الصين",
    "india": "الهند",
    "united kingdom": "المملكة المتحدة",
    "france": "فرنسا",
    "spain": "إسبانيا",
    "italy": "إيطاليا",
    "switzerland": "سويسرا",
    "austria": "النمسا",
    "germany": "ألمانيا",
    "netherlands": "هولندا",
    "greece": "اليونان",
    "bosnia and herzegovina": "البوسنة والهرسك",
    "albania": "ألبانيا",
    "united states": "الولايات المتحدة",
    "canada": "كندا",
}


def split_country(apps, schema_editor):
    Destination = apps.get_model("destinations", "Destination")
    for destination in Destination.objects.all().iterator():
        english = destination.country
        destination.country_en = english
        destination.country_ar = COUNTRY_AR.get(english.strip().lower(), english)
        destination.save(update_fields=["country_ar", "country_en"])


def merge_country(apps, schema_editor):
    """Reverse: the English column is the one the old single field held."""
    Destination = apps.get_model("destinations", "Destination")
    for destination in Destination.objects.all().iterator():
        destination.country = destination.country_en
        destination.save(update_fields=["country"])


class Migration(migrations.Migration):
    dependencies = [("destinations", "0002_alter_destination_cover_image")]

    operations = [
        # Give the old column a default before dropping it. Reversing a
        # RemoveField re-adds the column from migration state, and a NOT NULL
        # column with no default cannot be added to a table that already has
        # rows — without this the split would be a one-way door in production.
        migrations.AlterField(
            model_name="destination",
            name="country",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="destination",
            name="country_ar",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="destination",
            name="country_en",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.RunPython(split_country, merge_country),
        migrations.RemoveField(model_name="destination", name="country"),
    ]

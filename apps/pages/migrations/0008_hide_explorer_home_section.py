from django.db import migrations


def hide(apps, schema_editor):
    """Switched off for now — an editorial decision, not a deployment, so it
    lives here rather than in code. The component and its data stay exactly as
    they are; the panel's "Homepage sections" screen is a one-click undo.
    """
    apps.get_model("pages", "HomeSection").objects.filter(key="EXPLORER").update(
        is_active=False
    )


def unhide(apps, schema_editor):
    apps.get_model("pages", "HomeSection").objects.filter(key="EXPLORER").update(
        is_active=True
    )


class Migration(migrations.Migration):
    dependencies = [("pages", "0007_recommendations_home_section")]

    operations = [migrations.RunPython(hide, unhide)]

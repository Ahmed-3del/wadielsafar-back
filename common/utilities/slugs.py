from django.utils.text import slugify


def generate_unique_slug(instance, source_text, slug_field="slug"):
    """Slugify `source_text` and disambiguate with a numeric suffix against
    other rows of the same model, excluding the instance itself (for updates)."""
    model = instance.__class__
    base_slug = slugify(source_text)
    slug = base_slug
    suffix = 1
    while model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        suffix += 1
        slug = f"{base_slug}-{suffix}"
    return slug

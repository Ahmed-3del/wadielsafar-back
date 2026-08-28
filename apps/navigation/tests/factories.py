import factory

from apps.navigation.models import NavItem


class NavItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NavItem

    label_ar = factory.Sequence(lambda n: f"رابط {n}")
    label_en = factory.Sequence(lambda n: f"Link {n}")
    href = factory.Sequence(lambda n: f"/link-{n}")
    group = "PRIMARY"
    is_active = True

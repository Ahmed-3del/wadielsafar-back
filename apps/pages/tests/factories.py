import factory

from apps.pages.models import Page


class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Page

    name = factory.Sequence(lambda n: f"Page {n}")

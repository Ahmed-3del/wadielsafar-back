import factory

from apps.company.models import Branch, Certificate, SocialLink


class CertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Certificate

    name_ar = factory.Sequence(lambda n: f"شهادة {n}")
    name_en = factory.Sequence(lambda n: f"Certificate {n}")
    issuer_ar = "جهة إصدار"
    issuer_en = "Issuer"
    image = "https://cdn.example.com/badge.png"
    document = "https://cdn.example.com/certificate.pdf"
    is_active = True


class BranchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Branch

    name_ar = factory.Sequence(lambda n: f"فرع {n}")
    name_en = factory.Sequence(lambda n: f"Branch {n}")
    # Distinct per row: the seed migration keys on the number, and two branches
    # sharing one would make a test's intent ambiguous.
    phone = factory.Sequence(lambda n: f"+96611{n:07d}")
    is_active = True


class SocialLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialLink

    platform = "FACEBOOK"
    url = factory.Sequence(lambda n: f"https://facebook.com/profile{n}")
    is_active = True

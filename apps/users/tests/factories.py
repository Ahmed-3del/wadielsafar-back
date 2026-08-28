import factory

from apps.users.models import User
from common.constants import RoleChoices


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@wadi-elsafar.test")
    role = RoleChoices.SALES
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "default-pass-123")

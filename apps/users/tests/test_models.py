import pytest

from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


def test_user_str_returns_email():
    user = UserFactory(email="jane@example.com")
    assert str(user) == "jane@example.com"


def test_user_default_role_is_sales():
    user = UserFactory()
    assert user.role == RoleChoices.SALES


def test_email_is_the_username_field():
    assert UserFactory._meta.model.USERNAME_FIELD == "email"

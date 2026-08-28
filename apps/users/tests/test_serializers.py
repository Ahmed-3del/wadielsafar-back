import pytest

from apps.users.serializers import UserSerializer
from apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_user_serializer_excludes_password():
    user = UserFactory()
    data = UserSerializer(user).data
    assert "password" not in data
    assert data["email"] == user.email

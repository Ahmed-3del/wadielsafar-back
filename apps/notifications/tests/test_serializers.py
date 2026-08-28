import pytest

from apps.notifications.serializers import NotificationSerializer
from apps.notifications.tests.factories import NotificationFactory

pytestmark = pytest.mark.django_db


def test_notification_serializer_includes_name():
    obj = NotificationFactory(name="Sample Notification")
    data = NotificationSerializer(obj).data
    assert data["name"] == "Sample Notification"

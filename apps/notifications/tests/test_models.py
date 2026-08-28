import pytest

from apps.notifications.tests.factories import NotificationFactory

pytestmark = pytest.mark.django_db


def test_notification_str_returns_name():
    obj = NotificationFactory(name="Sample Notification")
    assert str(obj) == "Sample Notification"

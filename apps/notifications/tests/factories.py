import factory

from apps.notifications.models import Notification


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    name = factory.Sequence(lambda n: f"Notification {n}")

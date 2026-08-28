import django_filters

from apps.notifications.models import Notification


class NotificationFilter(django_filters.FilterSet):
    class Meta:
        model = Notification
        # No filterable fields yet — notifications is a Phase 1 scaffold; extend once
        # real business fields land.
        fields = ()

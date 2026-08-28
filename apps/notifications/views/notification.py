from rest_framework import viewsets

from apps.notifications.filters.notification_filter import NotificationFilter
from apps.notifications.models import Notification
from apps.notifications.permissions import NotificationPermission
from apps.notifications.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (NotificationPermission,)
    filterset_class = NotificationFilter
    search_fields = ("name",)

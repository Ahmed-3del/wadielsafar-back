from rest_framework import viewsets

from apps.users.models import User
from apps.users.permissions import IsStaffDirectoryReader
from apps.users.serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("email")
    serializer_class = UserSerializer
    permission_classes = (IsStaffDirectoryReader,)
    filterset_fields = ("role", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")

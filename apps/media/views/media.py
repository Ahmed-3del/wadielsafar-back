from rest_framework import mixins, viewsets

from apps.media.models import Media
from apps.media.permissions import MediaPermission
from apps.media.serializers import MediaSerializer


class MediaViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    # Destroy is included because editors upload the wrong file often enough
    # that a library without deletion just accumulates rubbish. There is no
    # update: replacing a file means uploading a new one, since anything
    # already pointing at the old URL would silently change.
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Media.objects.order_by("-created_at")
    serializer_class = MediaSerializer
    permission_classes = (MediaPermission,)

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

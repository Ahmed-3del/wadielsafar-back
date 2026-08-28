from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.testimonials.filters.testimonial_filter import TestimonialFilter
from apps.testimonials.models import Testimonial
from apps.testimonials.permissions import TestimonialPermission
from apps.testimonials.serializers import TestimonialSerializer
from apps.testimonials.services import TestimonialService
from common.constants import STAFF_CONTENT_ROLES


class TestimonialViewSet(viewsets.ModelViewSet):
    serializer_class = TestimonialSerializer
    permission_classes = (TestimonialPermission,)
    filterset_class = TestimonialFilter
    search_fields = ("customer_name", "content_ar", "content_en")
    ordering_fields = ("order", "rating", "created_at")

    def get_queryset(self):
        queryset = Testimonial.objects.all()
        user = self.request.user
        is_content_manager = user.is_authenticated and (
            user.is_superuser or user.role in STAFF_CONTENT_ROLES
        )
        if not is_content_manager:
            queryset = queryset.filter(is_approved=True, is_visible=True)
        return queryset

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        testimonial = TestimonialService.approve(self.get_object())
        serializer = TestimonialSerializer(testimonial, context={"request": request})
        return Response(serializer.data)

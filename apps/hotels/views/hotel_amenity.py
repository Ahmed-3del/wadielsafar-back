from rest_framework import viewsets

from apps.hotels.models import HotelAmenity
from apps.hotels.permissions import HotelPermission
from apps.hotels.serializers import HotelAmenitySerializer


class HotelAmenityViewSet(viewsets.ModelViewSet):
    queryset = HotelAmenity.objects.all()
    serializer_class = HotelAmenitySerializer
    permission_classes = (HotelPermission,)
    search_fields = ("name_ar", "name_en")
    ordering_fields = ("name_en",)

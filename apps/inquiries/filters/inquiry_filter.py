import django_filters

from apps.inquiries.models import Inquiry


class InquiryFilter(django_filters.FilterSet):
    class Meta:
        model = Inquiry
        fields = ("status", "service_type", "source", "destination")

from rest_framework import permissions, views
from rest_framework.response import Response

from apps.inquiries.models import InquiryServiceType
from apps.inquiries.serializers import ContactFormServiceSerializer
from apps.services.models import Service


class ContactFormServiceView(views.APIView):
    """What the contact form's "Service needed" list offers.

    Two sources, one list. The base types are the six an enquiry is filed
    under; the services are the ones an editor has switched on for the form,
    and they exist because "Other" is a bad answer to give someone who came
    for travel insurance.

    The services come after the types, in the Services screen's own order, so
    the form opens on flights rather than on whichever add-on sorts first.
    """

    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        entries = [
            {
                "kind": "TYPE",
                "value": row.value,
                "service_id": None,
                "slug": "",
                "label_ar": row.label_ar,
                "label_en": row.label_en,
                "order": row.order,
            }
            for row in InquiryServiceType.objects.filter(is_active=True)
        ]

        offset = len(entries) + 1
        entries += [
            {
                "kind": "SERVICE",
                # A service with no type of its own is still an enquiry, and
                # OTHER is the honest bucket for it.
                "value": service.service_type or "OTHER",
                "service_id": service.id,
                "slug": service.slug,
                "label_ar": service.name_ar,
                "label_en": service.name_en,
                "order": offset + index,
            }
            for index, service in enumerate(
                Service.objects.filter(is_active=True, is_on_contact_form=True)
            )
        ]

        return Response(ContactFormServiceSerializer(entries, many=True).data)

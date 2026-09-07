from rest_framework import serializers


class ContactFormServiceSerializer(serializers.Serializer):
    """One entry in the contact form's "what do you need?" list.

    The list has two sources — the six types every enquiry is filed under, and
    the services an editor has chosen to offer in their own right — and the
    form needs them as one ordered list. Merging them here rather than in the
    browser means one ordering, decided once.
    """

    # "TYPE" for one of the base service types, "SERVICE" for an entry from the
    # Services screen. The form sends back different things for each.
    kind = serializers.CharField()
    # The bucket the enquiry is filed under, either way.
    value = serializers.CharField()
    # Set only on a SERVICE, and what the form posts as `service`.
    service_id = serializers.IntegerField(allow_null=True)
    slug = serializers.CharField(allow_blank=True)
    label_ar = serializers.CharField()
    label_en = serializers.CharField()
    order = serializers.IntegerField()

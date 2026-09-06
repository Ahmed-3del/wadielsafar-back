from rest_framework import serializers

from apps.inquiries.models import InquiryField, split_options


class InquiryFieldSerializer(serializers.ModelSerializer):
    """The shape the website's contact form renders.

    `options` is served as a ready list of {value, label} pairs rather than the
    two blocks of text an editor types: zipping them is this end's job, and
    doing it here means the browser cannot get it wrong.
    """

    options = serializers.SerializerMethodField()

    class Meta:
        model = InquiryField
        fields = (
            "id",
            "service_type",
            "key",
            "label_ar",
            "label_en",
            "field_type",
            "placeholder_ar",
            "placeholder_en",
            "options_ar",
            "options_en",
            "options",
            "is_required",
            "order",
            "is_active",
        )
        read_only_fields = ("id",)

    def get_options(self, obj) -> list[dict]:
        arabic = split_options(obj.options_ar)
        english = split_options(obj.options_en)
        # Zipped by position, and the model's clean() is what keeps the two
        # lists the same length.
        return [{"ar": ar, "en": en} for ar, en in zip(arabic, english)]

    def validate(self, attrs):
        """Runs the model's own rules, which the panel would otherwise skip:
        ModelSerializer does not call full_clean()."""
        instance = InquiryField(**{**self._current(), **attrs})
        instance.clean()
        return attrs

    def _current(self) -> dict:
        if self.instance is None:
            return {}
        return {
            field.name: getattr(self.instance, field.name)
            for field in InquiryField._meta.fields
            if field.name != "id"
        }

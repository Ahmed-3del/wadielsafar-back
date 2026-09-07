from rest_framework import serializers

from apps.inquiries.models import InquiryField, split_options
from common.constants import ServiceTypeChoices


class InquiryFieldSerializer(serializers.ModelSerializer):
    """The shape the website's contact form renders.

    `options` is served as a ready list of {value, label} pairs rather than the
    two blocks of text an editor types: zipping them is this end's job, and
    doing it here means the browser cannot get it wrong.
    """

    options = serializers.SerializerMethodField()
    # Declared rather than inferred: a question attached to one service has no
    # type, and DRF makes a model ChoiceField required even when it is blankable.
    service_type = serializers.ChoiceField(
        choices=ServiceTypeChoices.choices, required=False, allow_blank=True, default=""
    )

    class Meta:
        model = InquiryField
        fields = (
            "id",
            "service_type",
            "service",
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
            "min_value",
            "max_value",
            "not_past",
            "not_before",
            "show_when_key",
            "show_when_value",
            "is_wide",
            "group_ar",
            "group_en",
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
        merged = {**self._current(), **attrs}
        instance = InquiryField(**merged)
        instance.clean()
        self._check_key_is_free(merged)
        return attrs

    def _check_key_is_free(self, merged: dict) -> None:
        """Asked here as well as by the database.

        The two unique constraints carry a condition, and DRF builds validators
        only from plain unique_together — so without this a duplicate key came
        back as a 500 from the database driver rather than as "that key is
        already taken" against the field that has it.
        """
        service = merged.get("service")
        if service is not None:
            clash = InquiryField.objects.filter(service=service, key=merged.get("key"))
            where = f"{service.name_en} already asks"
        else:
            clash = InquiryField.objects.filter(
                service__isnull=True,
                service_type=merged.get("service_type"),
                key=merged.get("key"),
            )
            where = "This service type already asks"
        if self.instance is not None:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError(
                {"key": f"{where} a question filed under \"{merged.get('key')}\"."}
            )

    def _current(self) -> dict:
        if self.instance is None:
            return {}
        return {
            field.name: getattr(self.instance, field.name)
            for field in InquiryField._meta.fields
            if field.name != "id"
        }

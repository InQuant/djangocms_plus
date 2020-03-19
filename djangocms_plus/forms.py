from collections import OrderedDict

from django import forms

from djangocms_plus.models import PlusPlugin


class PlusPluginBaseForm(forms.ModelForm):
    class Meta:
        model = PlusPlugin
        exclude = []

    def save(self, commit=False):
        obj = super().save(commit)
        obj.set_json(self.serialize_data())
        obj.save()
        return obj

    def serialize_data(self):
        parsed_data = OrderedDict()
        for key in self.fields.keys():
            value = self.cleaned_data.get(key)
            if key.startswith('_'):
                continue

            field = self.fields.get(key)
            if hasattr(field, "serialize_field") and callable(field.serialize_field):
                parsed_data[key] = field.serialize_field(value)
            else:
                parsed_data[key] = value
        return parsed_data

    @classmethod
    def deserialize(cls, obj):
        parsed_dict = OrderedDict()

        for field_name in cls.declared_fields:
            value = obj.get(field_name, None)
            if not value:
                continue

            field = cls.declared_fields.get(field_name)
            if hasattr(field, "deserialize_field"):
                deserialize_field = getattr(field, "deserialize_field")
                if callable(deserialize_field):
                    parsed_dict[field_name] = deserialize_field(value)
            else:
                parsed_dict[field_name] = value

        return parsed_dict

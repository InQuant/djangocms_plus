from collections import OrderedDict

from django import forms
from django.forms.utils import ErrorList

from djangocms_plus.models import PlusPlugin
import logging

logger = logging.getLogger(__name__)


class PlusPluginBaseForm(forms.ModelForm):
    """
    BaseForm for PluginForms.
    This ModelForm references to a PlusPlugin Model in order to write and read from the json (JSONField) attribute.
    """
    class Meta:
        model = PlusPlugin
        exclude = ["json"]  # Do not show json Field in Edit Form

    def save(self, commit=False):
        """
        Save data to json field after serializing it.
        :param commit:
        :return: Returns object
        :rtype: object
        """
        obj = super().save(commit)
        obj.json = self.serialize_data()
        obj.save()
        return obj

    def serialize_data(self):
        """
        Takes form field values and calls "serialize_field" method for each field,
        if it is declared in the field class.
        :return: Serialized data
        :rtype: dict
        """
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
        """
        Deserialize data from Json field into dict. Opposite of serialize function (see above)
        :param obj:
        :return: Data
        :rtype: dict
        """
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

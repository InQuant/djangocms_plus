from abc import abstractmethod, ABC

from django import forms


class BaseFieldMixIn(ABC):
    @abstractmethod
    def serialize_field(self, value):
        pass

    @abstractmethod
    def deserialize_field(self, value):
        pass


class PlusModelMultipleChoiceField(forms.ModelMultipleChoiceField, BaseFieldMixIn):
    def serialize_field(self, qs):
        return list(qs.values_list("pk", flat=True))

    def deserialize_field(self, value: list):
        return self.queryset.filter(pk__in=value)


class PlusModelChoiceField(forms.ModelChoiceField, BaseFieldMixIn):
    def serialize_field(self, obj: object):
        return getattr(obj, "pk", None)

    def deserialize_field(self, value):
        return self.queryset.get(pk=value)
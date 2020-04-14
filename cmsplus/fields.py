import re
from abc import abstractmethod, ABC

from cms.models.pagemodel import Page
from django import forms
from django.contrib.admin.sites import site as admin_site
from django.core.exceptions import ValidationError
from django.core.validators import ProhibitNullCharactersValidator
from django.db.models.fields.related import ManyToOneRel
from django.forms.fields import Field
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _, ugettext
from filer.fields.file import AdminFileWidget, FilerFileField
from filer.fields.image import FilerImageField
from filer.models.filemodels import File as FilerFileModel
from filer.models.imagemodels import Image as FilerImageModel


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


class PageChoiceIterator(forms.models.ModelChoiceIterator):
    ''' sort pages by absolute url
    '''
    def __iter__(self):
        pages = sorted(self.queryset.all(), key=lambda p: p.get_absolute_url())
        for obj in pages:
            yield self.choice(obj)

class PageSearchField(PlusModelChoiceField):
    iterator = PageChoiceIterator

    def __init__(self, *args, **kwargs):
        queryset = Page.objects.public()
        try:
            queryset = queryset.on_site(get_current_site())
        except:
            pass  # can happen if database is not ready yet
        kwargs.setdefault('queryset', queryset)
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        ''' display value is the absolute url, sorted via iterator above
        '''
        return obj.get_absolute_url()


class PlusFilerFileSearchField(PlusModelChoiceField):

    def __init__(self,
        queryset=FilerFileModel.objects.all(),
        widget=AdminFileWidget(
            ManyToOneRel(FilerFileField, FilerFileModel, 'id'), admin_site),
        *args, **kwargs):

        super().__init__(queryset=queryset, widget=widget, *args, **kwargs)

class PlusFilerImageSearchField(PlusModelChoiceField):

    def __init__(self,
        queryset=FilerImageModel.objects.all(),
        widget=AdminFileWidget(
            ManyToOneRel(FilerImageField, FilerImageModel, 'id'), admin_site),
        *args, **kwargs):

        super().__init__(queryset=queryset, widget=widget, *args, **kwargs)

# SizeField
# ---------
#
NUMBER_REGEX = r'^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)'
UNSIGNED_NUMBER_REGEX = r'^([0-9]+(\.[0-9]+)?|\.[0-9]+)'
NUMBER_PAT = re.compile(NUMBER_REGEX)

@deconstructible
class SizeUnitValidator():
    '''
    taken and adopted from cmsplugin_cascade.fields
    '''
    allowed_units = []
    message = _("'%(value)s' is not a valid size unit. Allowed units are: %(allowed_units)s.")
    code = 'invalid_size_unit'

    def __init__(self, allowed_units=None, allow_negative=True):
        possible_units = ['vw', 'vh', 'rem', 'px', 'em', '%', 'auto']
        if allowed_units is None:
            self.allowed_units = possible_units
        else:
            self.allowed_units = [au for au in allowed_units if au in possible_units]
        units_with_value = list(self.allowed_units)
        if 'auto' in self.allowed_units:
            self.allow_auto = True
            units_with_value.remove('auto')
        else:
            self.allow_auto = False
        if allow_negative:
            patterns = '{}({})$'.format(NUMBER_REGEX, '|'.join(units_with_value))
        else:
            patterns = '{}({})$'.format(UNSIGNED_NUMBER_REGEX, '|'.join(units_with_value))
        self.validation_pattern = re.compile(patterns)

    def __call__(self, value):
        if self.allow_auto and value == 'auto':
            return
        match = self.validation_pattern.match(value)
        if not (match and match.group(1).isdigit()):
            allowed_units = " {} ".format(ugettext("or")).join("'{}'".format(u) for u in self.allowed_units)
            params = {'value': value, 'allowed_units': allowed_units}
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.allowed_units == other.allowed_units and
            self.message == other.message and
            self.code == other.code
        )


class SizeField(Field):
    """
    Use this field for validating input containing a value ending in ``px``, ``em``, ``rem`` or ``%``.
    Use it for values representing a size, margin, padding, width or height.
    """

    def __init__(self, *, allowed_units=None, **kwargs):
        self.empty_value = ''
        super().__init__(**kwargs)
        self.validators.append(SizeUnitValidator(allowed_units))
        self.validators.append(ProhibitNullCharactersValidator())

    def to_python(self, value):
        """Return a stripped string."""
        if value not in self.empty_values:
            value = str(value).strip()
        if value in self.empty_values:
            return self.empty_value
        return value

    @staticmethod
    def get_number_part(value):
        m = NUMBER_PAT.search(value)
        try:
            return int(m.group())
        except ValueError:
            return float(m.group())

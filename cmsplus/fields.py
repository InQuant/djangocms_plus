from abc import abstractmethod, ABC

from django import forms
from django.contrib.admin.sites import site as admin_site
from django.db.models.fields.related import ManyToOneRel

from filer.models.filemodels import File as FilerFileModel
from filer.fields.file import AdminFileWidget, FilerFileField
from filer.models.imagemodels import Image as FilerImageModel
from filer.fields.image import AdminImageWidget, FilerImageField


from cms.models.pagemodel import Page

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

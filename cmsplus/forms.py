import logging
from collections import OrderedDict

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from cmsplus.app_settings import cmsplus_settings
from cmsplus.fields import (PageSearchField, PlusFilerFileSearchField, PlusFilerImageSearchField, KeyValueField)
from cmsplus.models import PlusPlugin

logger = logging.getLogger(__name__)


class PlusPluginFormBase(forms.ModelForm):
    """
    BaseForm for PluginForms.
    This ModelForm references to a PlusPlugin Model in order to write and read
    from the glossary (JSONField) attribute.
    """

    class Meta:
        model = PlusPlugin
        exclude = ["_json"]  # Do not show json Field in Edit Form

    def __init__(self, *args, **kwargs):

        if kwargs.get('instance'):
            # set form initial values as our instance model attributes are in
            # glossary not in the instance itself
            initial = kwargs.get('initial', {})

            for field_name, field in self.declared_fields.items():
                initial[field_name] = kwargs.get('instance').glossary.get(field_name)

            kwargs['initial'] = initial
        super(PlusPluginFormBase, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Put serialized data to glossary (_json) field, then save.
        """
        self.instance.data = self.serialize_data()
        return super(PlusPluginFormBase, self).save(commit)

    def serialize_data(self):
        """
        Takes form field values and calls "serialize_field" method for each field,
        if it is declared in the field class
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

    def deserialize(self):
        """
        Deserialize data from Json field into dict. Opposite of serialize function (see above)
        :return: Data
        :rtype: dict:
        """
        parsed_dict = OrderedDict()

        for field_name in self.declared_fields:
            value = self.data.get(field_name, None)

            field = self.declared_fields.get(field_name)
            if hasattr(field, "deserialize_field"):
                deserialize_field = getattr(field, "deserialize_field")
                if callable(deserialize_field):
                    try:
                        parsed_dict[field_name] = deserialize_field(value)
                    except ValidationError as e:
                        self._update_errors(e)
            else:
                parsed_dict[field_name] = value

        return parsed_dict


# StylePluginMixin form fields
# ----------------------------
#
def get_style_form_fields(style_config_key=None, style_multiple=False):
    """
    Use together with StylePluginMixin, e.g.

    class MyCustomForm(PlusPluginFormBase):
        ...  # form defs

        STYLE_CHOICES = 'MY_CUSTOM_STYLES'
        extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


    class MyCustomPlugin(StylePluginMixin, PlusPluginBase):
        name = _('My Custom')
        form = MyCustomForm
        render_template = 'custom/snippet.html'

    style_config_key should be a cmsplus_settings - key which holds the
    style choices, e.g.: ('c-text-white', 'Text White'), ...
    """
    style_choices = (
        ('', 'None'),
    )

    if style_config_key:
        sc = getattr(cmsplus_settings, style_config_key, style_choices)
    else:
        sc = style_choices

    if style_multiple:
        style_field = forms.MultipleChoiceField
    else:
        style_field = forms.ChoiceField

    return (
        style_field(
            label=_('Style'), required=False, choices=sc,
            initial=sc[0][0], help_text='Extra CSS predefined style class for plugin.'),
        forms.CharField(
            label=u'Extra Classes', required=False, initial='',
            widget=forms.widgets.TextInput(attrs={'style': 'width: 70vw'}),
            help_text='Extra CSS Classes (space separated) for plugin.'),
        forms.CharField(
            label=u'Label', required=False, initial='',
            help_text='Label to identify this plugin in page-structure.'),
        KeyValueField(
            label=u'Extra CSS', required=False, initial='',
            help_text='Add extra (device specific) css key, values, e.g: margin or margin:md or transform:xl'),
    )


# LinkFormBase
# ------------
#
class LinkFormBase(PlusPluginFormBase):
    """
    provides fields and methods which are needed to handle different link types.
    """
    LINK_TYPE_CHOICES = [
        ('cmspage', _("CMS Page")),
        ('download', _("Download File")),
        ('exturl', _("External URL")),
        ('email', _("Mail To")),
    ]

    link_type = forms.ChoiceField(
        label=_("Link"),
        help_text=_("Type of link"),
    )

    cms_page = PageSearchField(
        required=False,
        label='Internal Page',
        help_text=_("An internal link onto any CMS page."),
    )

    section = forms.CharField(
        required=False,
        label='Anchor',
        help_text=_("An anchor or bookmark on the internal linked page."),
    )

    ext_url = forms.CharField(
        required=False,
        label=_("URL"),
        help_text=_("Link onto external page"),
    )

    download_file = PlusFilerFileSearchField(
        label='Download file',
        required=False,
        help_text=_("An internal link onto a file from filer"),
    )
    file_as_page = forms.BooleanField(
        initial=False,
        label=_('Serve file as webpage'),
        required=False,
        help_text=_('e.g. PDF will be visible in browser instead of a download')
    )

    mail_to = forms.EmailField(
        required=False,
        label=_("Email"),
        help_text=_("Open Email program with this address"),
    )

    link_target = forms.ChoiceField(
        choices=[
            ('', _("Same Window")),
            ('_blank', _("New Window")),
            ('_parent', _("Parent Window")),
            ('_top', _("Topmost Frame")),
        ],
        label=_("Link Target"),
        required=False,
        help_text=_("Open Link in other target."),
    )

    link_title = forms.CharField(
        label=_("Link title"),
        required=False,
        help_text=_("Link's title"),
    )

    def __init__(self, *args, **kwargs):
        link_type_choices = []
        if not getattr(self, 'require_link', True):
            link_type_choices.append(('', _("No Link")))
            self.declared_fields['link_type'].required = False
        link_type_choices.extend(self.LINK_TYPE_CHOICES)
        self.declared_fields['link_type'].choices = link_type_choices
        self.declared_fields['link_type'].initial = link_type_choices[0][0]
        super(LinkFormBase, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(LinkFormBase, self).clean()
        link_type = cleaned_data.get('link_type')

        if link_type == 'cmspage' and not self.has_error('cms_page'):
            if not cleaned_data.get('cms_page'):
                error = ValidationError(_("CMS page to link to is missing."))
                self.add_error('cms_page', error)

        elif link_type == 'download' and not self.has_error('download_file'):
            if not cleaned_data.get('download_file'):
                error = ValidationError(_("File for download is missing."))
                self.add_error('download_file', error)

        elif link_type == 'exturl' and not self.has_error('ext_url'):
            if not cleaned_data.get('ext_url'):
                error = ValidationError(_("External link is missing."))
                self.add_error('ext_url', error)

        elif link_type == 'email' and not self.has_error('mail_to'):
            if not cleaned_data.get('mail_to'):
                error = ValidationError(_("Mailto link is missing."))
                self.add_error('mail_to', error)

        if self.errors:
            return None
        return cleaned_data


# image form fields
# -----------------
#
def get_image_form_fields(required=False, help_text=''):
    """
    Can be used to insert image form fields into the custom plugin form
    definition. call e.g.:
    image_file, image_title, image_alt = get_image_form_fields(required=True)
    """
    return (
       PlusFilerImageSearchField(
           label=_('Image File'),
           required=required,
           help_text=help_text
           ),

       forms.CharField(
           label=_('Image Title'),
           required=False,
           help_text=_(
               'Caption text added to the "title" attribute of the ' '<img> element.'),
           ),

       forms.CharField(
           label=_('Alternative Description'),
           required=False,
           help_text=_(
               'Textual description of the image added to the "alt" ' 'tag of the <img> element.'),
           )
       )

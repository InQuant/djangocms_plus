from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from django import forms

from cmsplus import app_settings as cmsplus_settings
from cmsplus.models import (PlusPlugin, LinkPluginMixin,)
from cmsplus.forms import (PlusPluginFormBase, LinkFormBase,
        get_style_form_fields)
from cmsplus.plugin_base import (PlusPluginBase, StylePluginMixin,
        LinkPluginBase)

# TextLinkPlugin
# --------------
#
class TextLinkPluginModel(PlusPlugin, LinkPluginMixin):
    class Meta:
        proxy = True


class TextLinkForm(LinkFormBase):

    link_content = forms.CharField(
        label=_("Link Content"),
        widget=forms.widgets.TextInput(attrs={'id': 'id_name'}),  # replace
        # auto-generated id so that CKEditor automatically transfers the text into
        # this input field
        help_text=_("Content of Link"),
    )


class TextLinkPlugin(LinkPluginBase):
    name = _("Link")
    model = TextLinkPluginModel
    form = TextLinkForm

    text_enabled = True
    render_template = 'cmsplus/generic/text-link.html'
    parent_classes = ['TextPlugin',]

    #class Media:
        #js = ['admin/js/jquery.init.js', 'cmsplus/js/admin/textlinkplugin.js']

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('link_content', ''))

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        """
        Workaround for `PluginPool.get_all_plugins()`, otherwise TextLinkPlugin is not allowed
        as a child of a `TextPlugin`.
        """
        # TODO: Check if still needed (it was from cascade)
        return False

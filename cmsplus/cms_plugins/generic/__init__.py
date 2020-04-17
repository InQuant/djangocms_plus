import sys

from django import forms
from django import template
from django.template.context import Context
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cmsplus.app_settings import cmsplus_settings as cps
from cmsplus.forms import (PlusPluginFormBase, LinkFormBase,
                           get_style_form_fields)
from cmsplus.models import (PlusPlugin, LinkPluginMixin, )
from cmsplus.plugin_base import (StylePluginMixin, PlusPluginBase, LinkPluginBase)


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
    parent_classes = ['TextPlugin', ]

    # class Media:
    #   js = ['admin/js/jquery.init.js', 'cmsplus/js/admin/textlinkplugin.js']

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


# MultiColTextPlugin
# ------------------
#
class MultiColTextForm(PlusPluginFormBase):
    STYLE_CHOICES = 'MOD_COL_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

    @staticmethod
    def _get_col_choice_field(dev):
        if dev == 'xs':
            choices = [('', '1 (default)'), ]
        else:
            choices = [('', 'inherit'), ]
        choices.extend(list(cps.TX_COL_CHOICES))

        field_name = 'col_%s' % dev
        field = forms.ChoiceField(
            label=u'%s No. of Cols' % cps.DEVICE_MAP[dev], required=False, choices=choices, initial='')
        return field_name, field

    @classmethod
    def extend_col_fields(cls):
        for dev in cps.DEVICES:
            field_name, field = cls._get_col_choice_field(dev)
            cls.declared_fields[field_name] = field


MultiColTextForm.extend_col_fields()


class MultiColumnTextPlugin(PlusPluginBase):
    footnote_html = """
    renders a wrapper for a multi column text.
    """
    name = _('MultiColumnText')
    form = MultiColTextForm
    render_template = "cmsplus/generic/multi-col-text.html"
    allow_children = True


# Snippet Plugin
# --------------
#
class SnippetForm(PlusPluginFormBase):

    html = forms.CharField(
        label=_('HTML'),
        widget=forms.Textarea(
            attrs={
                'rows': 15, 'data-editor': True,
                'data-mode': 'html', 'data-theme': 'default',
                'style': 'max-height: initial', 'class': 'c-border'}),
    )

    STYLE_CHOICES = 'SNIPPET_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)


class SnippetPlugin(StylePluginMixin, PlusPluginBase):
    footnote_html = """
    renders a given html snippet, can be used to include another site via iframe.
    """
    name = _('Snippet')
    form = SnippetForm
    allow_children = False
    render_template = 'cmsplus/generic/snippet/snippet.html'
    change_form_template = 'cmsplus/generic/snippet/change_form.html'

    text_enabled = True
    text_editor_preview = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        try:
            t = template.Template(instance.glossary.get('html'))
            content = t.render(Context(context))
        except Exception:
            exc = sys.exc_info()[0]
            content = str(exc)
        context['content'] = mark_safe(content)
        return context

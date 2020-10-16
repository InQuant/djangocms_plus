from django import forms
from django.utils.translation import ugettext_lazy as _

from cmsplus.forms import PlusPluginFormBase, get_style_form_fields
from cmsplus.plugin_base import PlusPluginBase, StylePluginMixin


class CardChildBaseForm(PlusPluginFormBase):
    element_id = forms.CharField(label=_('Element ID'), max_length=255, required=False)


class CardChildBase(PlusPluginBase):
    module = "Bootstrap"
    require_parent = True
    parent_classes = ['BootstrapCardPlugin']
    allow_children = True
    render_template = 'cmsplus/bootstrap/card/wrapper.html'


class CardHeaderForm(CardChildBaseForm):
    STYLE_CHOICES = 'CARD_HEADER_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapCardHeaderPlugin(StylePluginMixin, CardChildBase):
    name = _("Card Header")
    form = CardHeaderForm
    default_css_class = 'card-header'


class CardBodyForm(CardChildBaseForm):
    STYLE_CHOICES = 'CARD_BODY_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapCardBodyPlugin(StylePluginMixin, CardChildBase):
    name = _("Card Body")
    default_css_class = 'card-body'
    form = CardBodyForm


class CardFooterForm(CardChildBaseForm):
    STYLE_CHOICES = 'CARD_FOOTER_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapCardFooterPlugin(StylePluginMixin, CardChildBase):
    name = _("Card Footer")
    default_css_class = 'card-footer'
    form = CardFooterForm


class CardForm(CardChildBaseForm):
    STYLE_CHOICES = 'CARD_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapCardPlugin(StylePluginMixin, PlusPluginBase):
    """
    Use this plugin to display a card with optional card-header and card-footer.
    """
    module = "Bootstrap"
    name = _("Card")
    form = CardForm
    default_css_class = 'card'
    require_parent = False
    allow_children = True
    render_template = 'cmsplus/bootstrap/card/card.html'

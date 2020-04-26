from django.utils.translation import ugettext_lazy as _

from cmsplus.forms import PlusPluginFormBase, get_style_form_fields
from cmsplus.plugin_base import PlusPluginBase, StylePluginMixin


class CardChildForm(PlusPluginFormBase):
    STYLE_CHOICES = 'SLIDE_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class CardChildBase(PlusPluginBase):
    module = "Bootstrap"
    require_parent = True
    parent_classes = ['BootstrapCardPlugin']
    form = CardChildForm
    allow_children = True
    render_template = 'cmsplus/bootstrap/card/wrapper.html'


class BootstrapCardHeaderPlugin(StylePluginMixin, CardChildBase):
    name = _("Card Header")
    default_css_class = 'card-header'


class BootstrapCardBodyPlugin(StylePluginMixin, CardChildBase):
    name = _("Card Body")
    default_css_class = 'card-body'


class BootstrapCardFooterPlugin(StylePluginMixin, CardChildBase):
    name = _("Card Footer")
    default_css_class = 'card-footer'


class CardFormMixin(CardChildForm):
    STYLE_CHOICES = 'CARD_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapCardPlugin(StylePluginMixin, PlusPluginBase):
    """
    Use this plugin to display a card with optional card-header and card-footer.
    """
    module = "Bootstrap"
    form = CardFormMixin
    name = _("Card")
    default_css_class = 'card'
    require_parent = False
    allow_children = True
    render_template = 'cmsplus/bootstrap/card/card.html'

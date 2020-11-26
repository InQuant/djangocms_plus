from django import forms
from django.forms import widgets
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from cmsplus.forms import PlusPluginFormBase, get_style_form_fields
from cmsplus.plugin_base import PlusPluginBase, StylePluginMixin


class BootstrapAccordionPluginForm(PlusPluginFormBase):
    close_others = forms.BooleanField(
        label=_("Close others"),
        initial=True,
        required=False,
        help_text=_("Open only one card at a time.")
    )

    first_is_open = forms.BooleanField(
        label=_("First open"),
        initial=True,
        required=False,
        help_text=_("Start with the first card open.")
    )

    STYLE_CHOICES = 'ACCORDION_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapAccordionPlugin(StylePluginMixin, PlusPluginBase):
    footnote_html = """
    Renders a bootstrap accordion.
    """
    name = _("Accordion")
    module = 'Bootstrap'
    direct_child_classes = ['BootstrapAccordionGroupPlugin']
    allow_children = True
    form = BootstrapAccordionPluginForm
    render_template = 'cmsplus/bootstrap/accordion/accordion.html'

    fieldsets = (
        (None, {
            'fields': ('close_others', 'first_is_open', ),
        }),
        (_('Module settings'), {
            'classes': ('collapse',),
            'fields': (
                'extra_style', 'extra_classes', 'label',
            )
        }),
        (_('Extra CSS'), {
            'classes': ('collapse',),
            'fields': (
                'extra_css',
            )
        }),
    )

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context.update({
            'close_others': int(instance.glossary.get('close_others', True)),
            'first_is_open': instance.glossary.get('first_is_open', True),
        })
        return context


class BootstrapAccordionGroupForm(PlusPluginFormBase):
    heading = forms.CharField(
        label=_("Heading"),
        widget=widgets.TextInput(attrs={'size': 80}),
    )

    STYLE_CHOICES = 'ACCORDION_GROUP_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)

    def clean_heading(self):
        return escape(self.cleaned_data['heading'])


class BootstrapAccordionGroupPlugin(StylePluginMixin, PlusPluginBase):
    name = _("Accordion Group")
    module = 'Bootstrap'
    direct_parent_classes = parent_classes = ['BootstrapAccordionPlugin']
    render_template = 'cmsplus/bootstrap/accordion/accordion-group.html'
    require_parent = True
    form = BootstrapAccordionGroupForm
    alien_child_classes = True
    allow_children = True

    fieldsets = (
        (None, {
            'fields': ('heading', ),
        }),
        (_('Module settings'), {
            'fields': (
                'extra_style', 'extra_classes', 'label',
            )
        }),
        (_('Extra CSS'), {
            'classes': ('collapse',),
            'fields': (
                'extra_css',
            )
        }),
    )

    @staticmethod
    def is_closed(instance, parent_instance):
        if instance.position == 0 and parent_instance.glossary.get('first_is_open'):
            return False
        elif not parent_instance.glossary.get('close_others'):
            return False
        return True

    @classmethod
    def get_identifier(cls, instance):
        heading = instance.glossary.get('heading', '')
        return Truncator(heading).words(3, truncate=' ...')

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        parent_instance, parent_class = instance.parent.get_plugin_instance()

        context.update({
            'heading': mark_safe(instance.glossary.get('heading', '')),
            'parent_instance': parent_instance,
            'is_closed': self.is_closed(instance, parent_instance),
        })
        return context

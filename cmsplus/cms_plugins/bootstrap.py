from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminDateWidget

from django import forms

from cmsplus import app_settings as cmsplus_settings
from cmsplus.models import (PlusPlugin, LinkPluginMixin,)
from cmsplus.forms import (PlusPluginFormBase, LinkFormBase,
        get_style_form_fields)
from cmsplus.plugin_base import (PlusPluginBase, StylePluginMixin,
        LinkPluginBase)

from cmsplus.app_settings import (TEXT_COLOR_CHOICES, BG_COLOR_CHOICES,
        RL_MARGIN_CHOICES, TB_MARGIN_CHOICES, PADDING_CHOICES, DEVICE_MAP,
        DEVICE_MAX_WIDTH_MAP, DEVICE_MIN_WIDTH_MAP)

def get_devices():
    return cmsplus_settings.DEVICES

class BootstrapPluginBase(StylePluginMixin, PlusPluginBase):
    module = 'Bootstrap'

# MagicWrapper
# ------------
#
def get_choices(side, device, values):
    choices = []

    # e.g. g-ml, g-mb
    if device == 'xs':
        prefix = '%s' % side
        choices = [('', 'None',),]
    else:
        prefix = '%s-%s' % (side, device)
        choices = [('', 'inherit',),]

    for t in values:
        # v is a tuple e.g.  ('-1cw', '-1 Col'),
        v, d = t
        # e.g. g-ml--1cw, or: g-mb-16 or: g-pb-16
        choices.append(('g-%s-%s' % (prefix, v), d))
    return choices

def get_margin_choice_fields():
    sides = {'ml': 'left', 'mr': 'right', 'mt': 'top', 'mb': 'bottom'}
    choices = {'ml': RL_MARGIN_CHOICES, 'mr': RL_MARGIN_CHOICES,
            'mt': TB_MARGIN_CHOICES, 'mb': TB_MARGIN_CHOICES}
    for dev in get_devices():
        for side in ['ml', 'mr', 'mt', 'mb']:
            # e.g. label = 'left phone'
            key = '%s_%s' % (side, dev)
            label = '%s %s' % (sides[side], DEVICE_MAP[dev])

            field = forms.ChoiceField(label=label, required=False,
                    choices=get_choices(side, dev, choices[side]))
            yield key, field

def get_padding_choice_fields():
    sides = {'pl': 'left', 'pr': 'right', 'pt': 'top', 'pb': 'bottom'}
    for dev in get_devices():
        for side in ['pl', 'pr', 'pt', 'pb']:
            # e.g. label = 'left phone'
            key = '%s_%s' % (side, dev)
            label= '%s %s' % (sides[side], DEVICE_MAP[dev])

            field = forms.ChoiceField(label=label, required=False,
                    choices=get_choices(side, dev, PADDING_CHOICES))
            yield key, field

class MagicWrapperForm(PlusPluginFormBase):

    TAG_CHOICES = [(cls, _("<{}> – Element").format(cls)) for cls in ['div', 'span', 'section', 'article']]

    tag_type = forms.ChoiceField(
        choices=TAG_CHOICES,
        label=_("HTML element tag"),
        help_text=_('Choose a tag type for this HTML element.')
    )

    background_color = forms.ChoiceField(
        choices=BG_COLOR_CHOICES,
        label=_("Background Color"),
        required=False,
        help_text=_('Select a background color.')
    )

    # margin and padding fields are added in _extend_form_fields below

    STYLE_CHOICES = 'MAGIC_WRAPPER_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

    visible = forms.BooleanField(label=u'Visible', required=False, initial=True,
            help_text='Uncheck to hide wrapper with all of its childs.')
    vis_from = forms.DateField(label=u'Visible from', required=False, widget=AdminDateWidget(),
            help_text='Date when the wrapper with all of its childs will become visible.')
    vis_to = forms.DateField(label=u'Visible to', required=False, widget=AdminDateWidget(),
            help_text='Date when the wrapper with all of its childs will become invisible.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @staticmethod
    def get_margin_keys(for_dev=None):
        keys = []
        devs = for_dev or get_devices()
        for dev in devs:
            for s in ['ml', 'mr', 'mt', 'mb']:
                keys.append('%s_%s' % (s, dev))
        return keys

    @staticmethod
    def get_padding_keys(for_dev=None):
        keys = []
        devs = for_dev or get_devices()
        for dev in devs:
            for s in ['pl', 'pr', 'pt', 'pb']:
                keys.append('%s_%s' % (s, dev))
        return keys

    @classmethod
    def _extend_form_fields(cls):
        ''' Because margin and padding form fields have to be added dynamically
        to reflect the devices: xs - xl, xxl, ... configured in app_settings
        we get the MagicWrapperForm ready here... This method is called from
        module level below
        '''
        # add margin fields mt_xs, mr_xs .. ml_xl
        for field_name, field in get_margin_choice_fields():
            cls.declared_fields[field_name] = field

        # add padding fields pt_xs, pr_xs .. pl_xl
        for field_name, field in get_padding_choice_fields():
            cls.declared_fields[field_name] = field

# complete form fields with configured devices
MagicWrapperForm._extend_form_fields()


WF_MARGIN_KEYS = MagicWrapperForm.get_margin_keys
WF_PADDING_KEYS = MagicWrapperForm.get_padding_keys

class MagicWrapperPlugin(BootstrapPluginBase):
    footnote_html="""
    <p>renders a magic wrapper (e.g. div) which can be used to:</p>
    <ul>
    <li>- apply a chapter spacer</li>
    <li>- group child plugins</li>
    <li>- offset all childs in a specific direction. Offsets can be defined via Margins.</li>
    <li>- control visibility of all child plugins</li>
    <ul>
    <p>You may set the label for cms structure view.</p>
    """
    name = _('Wrapper')
    allow_children = True
    render_template = 'cmsplus/bootstrap/wrapper.html'
    css_class_fields = StylePluginMixin.css_class_fields + WF_MARGIN_KEYS() + WF_PADDING_KEYS() + [
            'background_color',]
    form = MagicWrapperForm

    fieldsets = [
        (None, {
            'fields': ('tag_type',),
        }),

        (_('Module settings'), {
            'fields': (
                'background_color',
                'extra_style',
                'extra_classes',
                'label',
            )
        }),

        (_('Visibility settings'), {
            'classes': ('collapse',),
            'fields': (
                'visible',
                'vis_from', 'vis_to',
            )
        }),

        (_('Margin settings'), {
            'classes': ('collapse',),
            'fields': [WF_MARGIN_KEYS(for_dev=[dev]) for dev in get_devices()],
        }),

        (_('Padding settings'), {
            'classes': ('collapse',),
            'fields': [WF_PADDING_KEYS(for_dev=[dev]) for dev in get_devices()],
        }),
    ]

    @classmethod
    def get_visibility(cls, instance):
        g = instance.glossary
        if not g.get('visible'): return False

        now = datetime.now().date()
        vis_from = dateutil.parser.parse(g['vis_from']).date() if g.get('vis_from') else now
        vis_to = dateutil.parser.parse(g['vis_to']).date() if g.get('vis_to') else now

        if vis_from <= now and now <= vis_to:
            return True
        return False

class BootstrapContainerPlugin(BootstrapPluginBase):
    name = 'Container'

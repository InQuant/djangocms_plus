from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminDateWidget

from django import forms

from cmsplus import app_settings as cmsplus_settings
from cmsplus.models import PlusPlugin
from cmsplus.forms import (PlusPluginFormBase, LinkFormBase,
        get_style_form_fields)
from cmsplus.plugin_base import (PlusPluginBase, StylePluginMixin,
        LinkPluginBase)

from cmsplus.app_settings import (TEXT_COLOR_CHOICES, BG_COLOR_CHOICES,
        RL_MARGIN_CHOICES, TB_MARGIN_CHOICES, PADDING_CHOICES, DEVICE_MAP,
        DEVICE_MAX_WIDTH_MAP, DEVICE_MIN_WIDTH_MAP, CNT_BOTTOM_MARGIN_CHOICES,
        ROW_BOTTOM_MARGIN_CHOICES, COL_BOTTOM_MARGIN_CHOICES, get_devices)

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
        we get the MagicWrapperForm ready here.This method is called from
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

        (_('Margin settings'), {
            'classes': ('collapse',),
            'fields': [WF_MARGIN_KEYS(for_dev=[dev]) for dev in get_devices()],
        }),

        (_('Padding settings'), {
            'classes': ('collapse',),
            'fields': [WF_PADDING_KEYS(for_dev=[dev]) for dev in get_devices()],
        }),
    ]


# BootstrapContainerForm
# ----------------------
#
class BootstrapContainerForm(PlusPluginFormBase):

    FLUID_CHOICES = (
        ('container', _('Fixed')),
        ('container-fluid', _('Fluid')),
    )
    fluid = forms.ChoiceField(
        label=_('Container Type'),
        initial='container',
        required=True,
        choices= FLUID_CHOICES,
        widget=forms.widgets.RadioSelect,
        help_text=_('Changing your container from "fixed content with fluid '
            'margin" to "fluid content with fixed margin".')
    )

    background_color = forms.ChoiceField(
        choices=BG_COLOR_CHOICES,
        label=_("Background Color"),
        required=False,
        help_text=_('Select a background color.')
    )

    bottom_margin = forms.ChoiceField(label=u'Bottom Margin',
            required=False, choices=CNT_BOTTOM_MARGIN_CHOICES,
            initial='',
            help_text='Select the default bottom margin to be applied?')

    STYLE_CHOICES = 'MOD_CONTAINER_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

class BootstrapContainerPlugin(BootstrapPluginBase):
    footnote_html="""
    renders a bootstrap container fix or fluid for device classes of:
     <ul>
     <li>XS: Portrait Phones (<576px)</li>
     <li>SM: Small Tablets  (≥576px and <768px)</li>
     <li>MD: Tablets (≥768px and <992px)</li>
     <li>LG: Laptops (≥992px and <1.200px)</li>
     <li>XL: Desktops (≥1.200px and <1.600px)</li>
     <li>2XL: Large Desktops (≥1.600px and < 1.900px)</li>
     <li>3XL: X-Large Desktops (≥1.920px)</li>
     <ul>
    """
    name = 'Container'
    form = BootstrapContainerForm
    allow_children = True
    parent_classes = None
    require_parent = False
    render_template = 'cmsplus/bootstrap/container.html'

    tag_type = 'div'
    css_class_fields = StylePluginMixin.css_class_fields + ['fluid',
            'background_color', 'bottom_margin']

    @classmethod
    def get_identifier(cls, instance):
        ident = super().get_identifier(instance)
        if not ident:
            cnt_info = dict(cls.form.FLUID_CHOICES)
            ident = cnt_info.get(instance.glossary.get('fluid'))
        return mark_safe(ident)


# BootstrapRowPlugin
# ------------------
#
class BootstrapRowForm(PlusPluginFormBase):

    bottom_margin = forms.ChoiceField(label=u'Bottom Margin',
            required=False, choices=ROW_BOTTOM_MARGIN_CHOICES,
            initial=ROW_BOTTOM_MARGIN_CHOICES[0][0],
            help_text='Select the default bottom margin to be applied?')

    STYLE_CHOICES = 'MOD_ROW_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

class BootstrapRowPlugin(BootstrapPluginBase):
    footnote_html="""
    renders a bootstrap (grid) row.
    """
    name = 'Row'
    form = BootstrapRowForm

    parent_classes = None
    require_parent = False
    allow_children = True

    render_template = 'cmsplus/bootstrap/row.html'

    tag_type = 'div'
    default_css_class = 'row'
    css_class_fields = StylePluginMixin.css_class_fields + ['bottom_margin',]


# BootstrapColForm
# ----------------
#
class ColDefHelper:

    def __init__(self, col_range=13, col_base=''):
        self.col_range = col_range
        self.col_base = col_base

    def get_dev_token(self, dev):
        ''' returns proper device token e.g.:  -xs or -md.
        '''
        return '-%s' % dev if dev != 'xs' else ''

    def get_col_choices(self, tok, attr, col_base=''):
        ''' returns choice tuples for given attr, e.g. col

        e.g. ('col-md-6', 'col 6')
        '''
        return [('col%s%s-%ld' % (col_base, tok, n), '%s %d' % (attr, n)) for n in range(1, self.col_range)]

    def get_attr_choices(self, tok, attr):
        return [('%s%s-%ld' % (attr, tok, n), '%s %d' % (attr, n)) for n in range(1, self.col_range)]

    def col_width_choices(self, dev):
        '''
        return tuples of ('col-md-1', 'col 1')
        '''
        tok = self.get_dev_token(dev)

        if dev == 'xs':
            choices = [('', 'flex'),]
        else:
            choices = [('', 'inherit'),]
            choices.append(('col%s%s' % (self.col_base, tok), 'flex'))

        choices.extend(self.get_col_choices(tok, 'col', col_base=self.col_base))
        choices.append(('col%s%s-auto' % (self.col_base, tok), 'auto'))
        return choices

    def col_offset_choices(self, dev):
        '''
        return tuples of ('offset-md-1', 'offset 1')
        '''
        tok = self.get_dev_token(dev)
        if dev == 'xs':
            choices = [('', 'none'),]
        else:
            choices = [('', 'inherit'),]
        choices.extend(self.get_attr_choices(tok, 'offset'))
        return choices

    def col_order_choices(self, dev):
        '''
        return tuples of ('order-md-1', 'order 1')
        '''
        tok = self.get_dev_token(dev)
        if dev == 'xs':
            choices = [('', 'none'),]
        else:
            choices = [('', 'inherit'),]
        choices.append(('order%s-first' % tok, 'first'))
        choices.extend(self.get_attr_choices(tok, 'order'))
        choices.append(('order%s-last' % tok, 'last'))
        return choices

    def col_display_choices(self, dev):
        '''
        return tuples of ('d-*-block', 'd-block')
        '''
        DISPLAY_VALUES = ['block', 'flex', 'inline', 'inline-block', 'none', 'table', 'table-cell']
        tok = self.get_dev_token(dev)
        if dev == 'xs':
            choices = [('', 'not set'),]
        else:
            choices = [('', 'inherit'),]

        for v in DISPLAY_VALUES:
            choices.append(('d%s-%s' % (tok, v), '%s' % v),)
        return choices


    def get_column_form_fields(self, attrs=[], initials={}, choices={}):
        _attrs = attrs or ['offset', 'width', 'order', 'display']

        for attr in _attrs:
            for dev in get_devices():
                field_name = 'col_%s_%s' % (attr, dev)

                choice_method = getattr(self, 'col_%s_choices' % attr)
                attr_choices = choices.get(attr, {}).get(dev, choice_method(dev))

                # e.g. label = 'left phone'
                label= '%s %s' % (DEVICE_MAP[dev], attr)

                if attr == 'width' and dev == 'xs':
                    field = forms.ChoiceField(
                            label=label, required=False,
                            choices=attr_choices,
                            initial=initials.get(attr, {}).get(dev, 'col'))
                else:
                    field = forms.ChoiceField(label=label, required=False,
                            choices=attr_choices,
                            initial=initials.get(attr, {}).get(dev, ''))

                field_name = 'col_%s_%s' % (attr, dev)
                yield field_name, field

class BootstrapColumnForm(PlusPluginFormBase):

    bottom_margin = forms.ChoiceField(label=u'Bottom Margin',
            required=False, choices=COL_BOTTOM_MARGIN_CHOICES,
            initial=COL_BOTTOM_MARGIN_CHOICES[0][0],
            help_text='Select the default bottom margin to be applied')

    STYLE_CHOICES = 'MOD_COL_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

    # offset and width fields are dynamically added with _extend_form_fields
    # method below

    @staticmethod
    def get_column_keys(for_attrs=None):
        keys = []
        attrs = for_attrs or ['offset', 'width', 'order', 'display']
        for attr in attrs:
            for dev in get_devices():
                keys.append('col_%s_%s' % (attr, dev))
        return keys

    @classmethod
    def _extend_form_fields(cls, col_helper):
        ''' Because column size form fields have to be added dynamically
        to reflect the devices: xs - xl, xxl, ... configured in app_settings
        we get the form ready here. This method is called from
        module level below
        '''
        # add column size fields col_offset_xs ..., col_width_xs ..,
        # col_order_xs.., col_display_xs .. col_display_xl
        for field_name, field in col_helper.get_column_form_fields():
            cls.declared_fields[field_name] = field

BootstrapColumnForm._extend_form_fields(
        ColDefHelper(col_range=13, col_base='')) # default 12 divided form

MCF_COLUMN_KEYS = BootstrapColumnForm.get_column_keys

class BootstrapColPlugin(BootstrapPluginBase):
    footnote_html="""
    renders a bootstrap column with variable offset and with.
    """
    name = _('Column')
    form = BootstrapColumnForm
    allow_children = True
    parent_classes = None
    require_parent = False
    render_template = 'cmsplus/bootstrap/column.html'

    tag_type = 'div'
    default_css_class = 'col'
    css_class_fields = StylePluginMixin.css_class_fields + MCF_COLUMN_KEYS(
            ) + ['bottom_margin']

    fieldsets = [
        (_('Column settings'), {
            'fields': (
                MCF_COLUMN_KEYS(for_attrs=['offset',]),
                MCF_COLUMN_KEYS(for_attrs=['width',]),
            )
        }),
        (_('Extra Column settings'), {
            'classes': ('collapse',),
            'fields': (
                MCF_COLUMN_KEYS(for_attrs=['order',]),
                MCF_COLUMN_KEYS(for_attrs=['display',]),
            )
        }),
        (_('Module settings'), {
            'fields': (
                'bottom_margin',
                'label',
                'extra_style',
                'extra_classes',
            )
        }),
    ]

# 10 divided column form and plugin
# ---------------------------------
class BootstrapCol10Form(BootstrapColumnForm):
    ''' 10 divided column form.
    '''

BootstrapCol10Form._extend_form_fields(
        ColDefHelper(col_range=11, col_base='10'))


class BootstrapCol10Plugin(BootstrapColPlugin):
    footnote_html="""
    renders a bootstrap 10 divided column with variable offset and with.
    """
    name = _('Column 1/10')
    form = BootstrapCol10Form

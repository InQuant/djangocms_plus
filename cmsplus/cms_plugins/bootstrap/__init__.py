import logging
import urllib.parse

from django import forms
from django.forms import widgets
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cmsplus.app_settings import cmsplus_settings as cps
from cmsplus.cms_plugins.generic.icon import IconField, get_icon_style_paths
from cmsplus.fields import SizeField, PlusFilerImageSearchField
from cmsplus.forms import (PlusPluginFormBase, LinkFormBase, get_style_form_fields, get_image_form_fields)
from cmsplus.models import PlusPlugin, LinkPluginMixin
from cmsplus.plugin_base import (PlusPluginBase, StylePluginMixin, LinkPluginBase)

logger = logging.getLogger(__name__)


class BootstrapPluginBase(StylePluginMixin, PlusPluginBase):
    module = 'Bootstrap'


# MagicWrapper
# ------------
#
def get_choices(side, device, values):
    # e.g. g-ml, g-mb
    if device == 'xs':
        prefix = '%s' % side
        choices = [('', 'None',), ]
    else:
        prefix = '%s-%s' % (side, device)
        choices = [('', 'inherit',), ]

    for t in values:
        # v is a tuple e.g.  ('-1cw', '-1 Col'),
        v, d = t
        # e.g. g-ml--1cw, or: g-mb-16 or: g-pb-16
        choices.append(('g-%s-%s' % (prefix, v), d))
    return choices


def get_margin_choice_fields():
    sides = {'ml': 'left', 'mr': 'right', 'mt': 'top', 'mb': 'bottom'}
    choices = {'ml': cps.RL_MARGIN_CHOICES, 'mr': cps.RL_MARGIN_CHOICES,
               'mt': cps.TB_MARGIN_CHOICES, 'mb': cps.TB_MARGIN_CHOICES}
    for dev in cps.DEVICES:
        for side in ['ml', 'mr', 'mt', 'mb']:
            # e.g. label = 'left phone'
            key = '%s_%s' % (side, dev)
            label = '%s %s' % (sides[side], cps.DEVICE_MAP[dev])

            field = forms.ChoiceField(
                label=label, required=False,
                choices=get_choices(side, dev, choices[side]))
            yield key, field


def get_padding_choice_fields():
    sides = {'pl': 'left', 'pr': 'right', 'pt': 'top', 'pb': 'bottom'}
    for dev in cps.DEVICES:
        for side in ['pl', 'pr', 'pt', 'pb']:
            # e.g. label = 'left phone'
            key = '%s_%s' % (side, dev)
            label = '%s %s' % (sides[side], cps.DEVICE_MAP[dev])

            field = forms.ChoiceField(
                label=label, required=False,
                choices=get_choices(side, dev, cps.PADDING_CHOICES))
            yield key, field


class MagicWrapperForm(PlusPluginFormBase):

    TAG_CHOICES = [(cls, _("<{}> – Element").format(cls)) for cls in ['div', 'span', 'section', 'article']]

    tag_type = forms.ChoiceField(
        choices=TAG_CHOICES,
        label=_("HTML element tag"),
        help_text=_('Choose a tag type for this HTML element.')
    )

    background_color = forms.ChoiceField(
        choices=cps.BG_COLOR_CHOICES,
        label=_("Background Color"),
        required=False,
        help_text=_('Select a background color.')
    )

    # margin and padding fields are added in _extend_form_fields below

    element_id = forms.CharField(label=_('Element ID'), max_length=255, required=False)

    STYLE_CHOICES = 'MAGIC_WRAPPER_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(MagicWrapperForm, self).__init__(*args, **kwargs)

    @staticmethod
    def get_margin_keys(for_dev=None):
        keys = []
        devs = for_dev or cps.DEVICES
        for dev in devs:
            for s in ['ml', 'mr', 'mt', 'mb']:
                keys.append('%s_%s' % (s, dev))
        return keys

    @staticmethod
    def get_padding_keys(for_dev=None):
        keys = []
        devs = for_dev or cps.DEVICES
        for dev in devs:
            for s in ['pl', 'pr', 'pt', 'pb']:
                keys.append('%s_%s' % (s, dev))
        return keys

    @classmethod
    def _extend_form_fields(cls):
        """ Because margin and padding form fields have to be added dynamically
        to reflect the devices: xs - xl, xxl, ... configured in app_settings
        we get the MagicWrapperForm ready here.This method is called from
        module level below.
        """
        # add margin fields mt_xs, mr_xs ... ml_xl
        for field_name, field in get_margin_choice_fields():
            cls.declared_fields[field_name] = field

        # add padding fields pt_xs, pr_xs ... pl_xl
        for field_name, field in get_padding_choice_fields():
            cls.declared_fields[field_name] = field


# complete form fields with configured devices
MagicWrapperForm._extend_form_fields()


WF_MARGIN_KEYS = MagicWrapperForm.get_margin_keys
WF_PADDING_KEYS = MagicWrapperForm.get_padding_keys


class MagicWrapperPlugin(BootstrapPluginBase):
    footnote_html = """
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
        'background_color', ]
    form = MagicWrapperForm

    fieldsets = [
        (None, {
            'fields': ('tag_type', 'element_id'),
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
            'fields': [WF_MARGIN_KEYS(for_dev=[dev]) for dev in cps.DEVICES],
        }),

        (_('Padding settings'), {
            'classes': ('collapse',),
            'fields': [WF_PADDING_KEYS(for_dev=[dev]) for dev in cps.DEVICES],
        }),
        (_('Extra CSS'), {
            'classes': ('collapse',),
            'fields': (
                'extra_css',
            )
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
        choices=FLUID_CHOICES,
        widget=forms.widgets.RadioSelect,
        help_text=_('Changing your container from "fixed content with fluid '
                    'margin" to "fluid content with fixed margin".')
    )

    background_color = forms.ChoiceField(
        choices=cps.BG_COLOR_CHOICES,
        label=_("Background Color"),
        required=False,
        help_text=_('Select a background color.')
    )

    bottom_margin = forms.ChoiceField(
        label=u'Bottom Margin',
        required=False, choices=cps.CNT_BOTTOM_MARGIN_CHOICES,
        initial='',
        help_text='Select the default bottom margin to be applied?')

    STYLE_CHOICES = 'MOD_CONTAINER_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapContainerPlugin(BootstrapPluginBase):
    footnote_html = """
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
    css_class_fields = StylePluginMixin.css_class_fields + [
        'fluid', 'background_color', 'bottom_margin']

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

    bottom_margin = forms.ChoiceField(
        label=u'Bottom Margin',
        required=False, choices=cps.ROW_BOTTOM_MARGIN_CHOICES,
        initial=cps.ROW_BOTTOM_MARGIN_CHOICES[0][0],
        help_text='Select the default bottom margin to be applied?')

    STYLE_CHOICES = 'MOD_ROW_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapRowPlugin(BootstrapPluginBase):
    footnote_html = """
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
    css_class_fields = StylePluginMixin.css_class_fields + ['bottom_margin', ]


# BootstrapColForm
# ----------------
#
class ColDefHelper:

    def __init__(self, col_range=13, col_base=''):
        self.col_range = col_range
        self.col_base = col_base

    @staticmethod
    def get_dev_token(dev):
        """
        Returns proper device token e.g.:  -xs or -md.
        """
        return '-%s' % dev if dev != 'xs' else ''

    def get_col_choices(self, tok, attr, col_base=''):
        """ Returns choice tuples for given attr, e.g. col
        e.g. ('col-md-6', 'col 6').
        """
        return [('col%s%s-%ld' % (col_base, tok, n), '%s %d' % (attr, n)) for n in range(1, self.col_range)]

    def get_attr_choices(self, tok, attr):
        return [('%s%s-%ld' % (attr, tok, n), '%s %d' % (attr, n)) for n in range(1, self.col_range)]

    def col_width_choices(self, dev):
        """
        Return tuples of ('col-md-1', 'col 1')
        """
        tok = self.get_dev_token(dev)

        if dev == 'xs':
            choices = [('', 'flex'), ]
        else:
            choices = [('', 'inherit'), ('col%s%s' % (self.col_base, tok), 'flex')]

        choices.extend(self.get_col_choices(tok, 'col', col_base=self.col_base))
        choices.append(('col%s%s-auto' % (self.col_base, tok), 'auto'))
        return choices

    def col_offset_choices(self, dev):
        """
        Return tuples of ('offset-md-1', 'offset 1').
        """
        tok = self.get_dev_token(dev)
        if dev == 'xs':
            choices = [('', 'none'), ]
        else:
            choices = [('', 'inherit'), ]
        choices.extend(self.get_attr_choices(tok, 'offset'))
        return choices

    def col_order_choices(self, dev):
        """
        Return tuples of ('order-md-1', 'order 1')
        """
        tok = self.get_dev_token(dev)
        if dev == 'xs':
            choices = [('', 'none'), ]
        else:
            choices = [('', 'inherit'), ]
        choices.append(('order%s-first' % tok, 'first'))
        choices.extend(self.get_attr_choices(tok, 'order'))
        choices.append(('order%s-last' % tok, 'last'))
        return choices

    def col_display_choices(self, dev):
        """
        Return tuples of ('d-*-block', 'd-block').
        """
        display_values = ['block', 'flex', 'inline', 'inline-block', 'none', 'table', 'table-cell']
        tok = self.get_dev_token(dev)
        if dev == 'xs':
            choices = [('', 'not set'), ]
        else:
            choices = [('', 'inherit'), ]

        for v in display_values:
            choices.append(('d%s-%s' % (tok, v), '%s' % v),)
        return choices

    def get_column_form_fields(self, attrs=None, initials=None, choices=None):
        attrs = [] if not attrs else attrs
        initials = {} if not initials else initials
        choices = {} if not choices else choices

        _attrs = attrs or ['offset', 'width', 'order', 'display']

        for attr in _attrs:
            for dev in cps.DEVICES:
                choice_method = getattr(self, 'col_%s_choices' % attr)
                attr_choices = choices.get(attr, {}).get(dev, choice_method(dev))

                # e.g. label = 'left phone'
                label = '%s %s' % (cps.DEVICE_MAP[dev], attr)

                if attr == 'width' and dev == 'xs':
                    field = forms.ChoiceField(
                        label=label, required=False,
                        choices=attr_choices,
                        initial=initials.get(attr, {}).get(dev, 'col'))
                else:
                    field = forms.ChoiceField(
                        label=label, required=False,
                        choices=attr_choices,
                        initial=initials.get(attr, {}).get(dev, ''))

                field_name = 'col_%s_%s' % (attr, dev)
                yield field_name, field


class BootstrapColumnForm(PlusPluginFormBase):

    bottom_margin = forms.ChoiceField(
        label=u'Bottom Margin',
        required=False, choices=cps.COL_BOTTOM_MARGIN_CHOICES,
        initial=cps.COL_BOTTOM_MARGIN_CHOICES[0][0],
        help_text='Select the default bottom margin to be applied')

    STYLE_CHOICES = 'MOD_COL_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)

    # offset and width fields are dynamically added with _extend_form_fields
    # method below

    @staticmethod
    def get_column_keys(for_attrs=None):
        keys = []
        attrs = for_attrs or ['offset', 'width', 'order', 'display']
        for attr in attrs:
            for dev in cps.DEVICES:
                keys.append('col_%s_%s' % (attr, dev))
        return keys

    # noinspection GrazieInspection
    @classmethod
    def extend_form_fields(cls, col_helper):
        """ Because column size form fields have to be added dynamically
        to reflect the devices: xs - xl, xxl, ... configured in app_settings
        we get the form ready here. This method is called from
        module level below.
        """
        # add column size fields col_offset_xs ..., col_width_xs ...,
        # col_order_xs.., col_display_xs .. col_display_xl
        for field_name, field in col_helper.get_column_form_fields():
            cls.declared_fields[field_name] = field


BootstrapColumnForm.extend_form_fields(ColDefHelper(col_range=13, col_base=''))  # default 12 divided form

MCF_COLUMN_KEYS = BootstrapColumnForm.get_column_keys


class BootstrapColPlugin(BootstrapPluginBase):
    footnote_html = """
    Renders a bootstrap column with variable offset and with.
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
                MCF_COLUMN_KEYS(for_attrs=['offset', ]),
                MCF_COLUMN_KEYS(for_attrs=['width', ]),
            )
        }),
        (_('Extra Column settings'), {
            'classes': ('collapse',),
            'fields': (
                MCF_COLUMN_KEYS(for_attrs=['order', ]),
                MCF_COLUMN_KEYS(for_attrs=['display', ]),
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
        (_('Extra CSS'), {
            'classes': ('collapse',),
            'fields': (
                'extra_css',
            )
        }),
    ]


# 10 divided column form and plugin
# ---------------------------------
class BootstrapCol10Form(BootstrapColumnForm):
    """
    10 divided column form.
    """


BootstrapCol10Form.extend_form_fields(ColDefHelper(col_range=11, col_base='10'))


class BootstrapCol10Plugin(BootstrapColPlugin):
    footnote_html = """
    renders a bootstrap 10 divided column with variable offset and with.
    """
    name = _('Column 1/10')
    form = BootstrapCol10Form


# Image Plugin
# ------------
#
def get_img_dev_width_fields(initials=None):
    initials = {} if not initials else initials
    for dev in cps.DEVICES:

        # e.g. label = 'phone width'
        label = '%s Width' % cps.DEVICE_MAP[dev].title()

        if dev == 'xs':
            field = forms.ChoiceField(
                label=label,
                choices=cps.IMG_DEV_WIDTH_CHOICES,
                initial=initials.get('xs', '1/2'))
        else:
            field = forms.ChoiceField(
                label=label,
                required=False,
                choices=[('', 'inherit'), ] + list(cps.IMG_DEV_WIDTH_CHOICES),
                initial=initials.get(dev, ''))

        field_name = 'img_dev_width_%s' % dev
        yield field_name, field


def get_fixed_dim_fields(attr):
    for dev in cps.DEVICES:
        # e.g. fixed_width_xs

        # e.g. label = 'phone width'
        label = '%s %s' % (cps.DEVICE_MAP[dev].title(), attr.title())

        field = SizeField(
            label=_(label),
            required=False,
            allowed_units=['px', '%', 'rem', 'vw', 'vh'],
            initial='',
        )
        field_name = 'fixed_%s_%s' % (attr, dev)
        yield field_name, field


class BootstrapImageForm(LinkFormBase):

    image_file, image_title, image_alt = get_image_form_fields(required=True)

    STYLE_CHOICES = 'IMAGE_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)

    require_link = False

    SHAPE_CHOICES = [
        ('', _('None')),
        ('rounded', _('Rounded')),
        ('rounded-circle', _('Circle')),
        ('img-thumbnail', _('Thumbnail')),
    ]
    image_shapes = forms.ChoiceField(
        label=_("Image Shapes"),
        choices=SHAPE_CHOICES,
        required=False,
        initial=''
    )

    ALIGNMENT_OPTIONS = [
        ('', _("None")),
        ('float-left', _("Left")),
        ('float-right', _("Right")),
        ('mx-auto', _("Center")),
    ]
    image_alignment = forms.ChoiceField(
        label=_("Image Alignment"),
        choices=ALIGNMENT_OPTIONS,
        required=False,
        initial='',
        help_text=_("How to align the image (this choice only applies if the image is fixed size (none repsonsive)."),
    )

    # fixed width and height fields are added with _extend_form_fields below

    RESIZE_OPTIONS = [
        ('crop', _("Crop image")),
        ('upscale', _("Upscale image")),
    ]
    resize_options = forms.MultipleChoiceField(
        label=_("Resize Options"),
        choices=RESIZE_OPTIONS,
        widget=forms.widgets.CheckboxSelectMultiple,
        required=True,
        initial=['crop'],
        help_text=_("Options to use when calculating the cached size device specific version of the image."),
    )

    # img_dev_width fields are added with _extend_form_fields below

    @classmethod
    def extend_form_fields(cls):
        for field_name, field in get_fixed_dim_fields('width'):
            cls.declared_fields[field_name] = field
        for field_name, field in get_fixed_dim_fields('height'):
            cls.declared_fields[field_name] = field
        for field_name, field in get_img_dev_width_fields():
            cls.declared_fields[field_name] = field


BootstrapImageForm.extend_form_fields()


class BootstrapImagePluginModel(PlusPlugin, LinkPluginMixin):
    class Meta:
        proxy = True


class BootstrapImagePlugin(StylePluginMixin, LinkPluginBase):
    footnote_html = """
        renders a bootstrap responsive (fluid) image.
    """
    name = 'Image'
    model = BootstrapImagePluginModel
    form = BootstrapImageForm
    parent_classes = None
    require_parent = False

    text_enabled = True  # enable in CK_EDITOR
    render_template = 'cmsplus/bootstrap/image.html'

    default_css_class = 'img-fluid'
    css_class_fields = StylePluginMixin.css_class_fields + [
        'image_shapes', 'image_alignment']
    tag_attr_map = {'image_title': 'title', 'image_alt': 'alt'}

    fieldsets = [
        (None, {
            'fields': ('image_file', 'image_title', 'image_alt'),
        }),
        (_('Shape and alignment settings'), {
            'classes': ('collapse',),
            'fields': (
                ('image_shapes', 'image_alignment',),
            )
        }),
        (_('Fixed Dimension'), {
            'classes': ('collapse',),
            'description': _('Set one or both image dimensions to fixed [px, %, rem, vw, vh].'),
            'fields': (
                [field_name for field_name, field in get_fixed_dim_fields('width')],
                [field_name for field_name, field in get_fixed_dim_fields('height')],
            ),
        }),
        (_('Responsive options'), {
            'classes': ('collapse',),
            'description': _(
                'Maximum responsive width per device if no fixed '
                '(px) width or height given. Used to provide optimal image size '
                'for each device with respect to loading time.'),
            'fields': (
                [field_name for field_name, field in get_img_dev_width_fields()],
                ('resize_options',),
            ),
        }),
        (_('Module settings'), {
            'classes': ('collapse',),
            'fields': (
                'extra_style', 'extra_classes', 'label',
            )
        }),
        (_('Link settings'), {
            'classes': ('collapse',),
            'fields': (
                'link_type', 'cms_page', 'section', 'download_file', 'file_as_page', 'ext_url',
                'mail_to', 'link_target', 'link_title'
            )
        }),
        (_('Extra CSS'), {
            'classes': ('collapse',),
            'fields': (
                'extra_css',
            )
        }),
    ]

    @classmethod
    def get_identifier(cls, instance):
        try:
            name = str(instance.glossary.get('image_file'))
        except AttributeError:
            name = _("No Image")
        return mark_safe(name)

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        glossary = instance.glossary
        if not glossary.get('image_file'):
            logger.error(_('Filer image not found for instance id: %s' % instance.id))
            return

        media_queries, easy_thumb_sizes = self._get_media_sizes(instance)

        # no srcsets for gifs
        if glossary.get('image_file'):
            _file = glossary.get('image_file')
            if _file.extension == 'gif':
                context['is_gif'] = True
                return context

        # srcset sizes
        context['sizes'] = [media_queries[dev] for dev in cps.DEVICES]

        # srcset
        srcset = {}
        v = None
        for dev in cps.DEVICES:
            # e.g. srcset['320w'] = '320x200'
            k = '%dw' % easy_thumb_sizes[dev][0]
            v = '%dx%d' % (easy_thumb_sizes[dev][0], easy_thumb_sizes[dev][1])
            srcset[k] = v

        context['srcset'] = srcset
        context['src_size'] = v

        # crop / upscale options
        context['crop'] = 'crop' in glossary.get('resize_options')
        context['upscale'] = 'upscale' in glossary.get('resize_options')

        # scoped styles
        scopedstyles = {}
        fixed_sizes = self._get_fixed_sizes(instance)
        if len(fixed_sizes.keys()) == 1 and 'xs' in fixed_sizes.keys():
            pass  # no scoped style neeed - see get_inline_styles
        else:
            for dev in cps.DEVICES:
                if fixed_sizes.get(dev):
                    k = cps.DEVICE_MIN_WIDTH_MAP.get(dev)
                    scopedstyles[k] = (
                        fixed_sizes[dev].get('width'),
                        fixed_sizes[dev].get('height'))
        context['scopedstyles'] = scopedstyles

        return context

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = super().get_inline_styles(instance)

        # if only xs is in fixed_sizes, we don't need scoped styles
        # (see render) as we don't have any media settings in this case
        fs = cls._get_fixed_sizes(instance)
        if len(fs.keys()) == 1 and 'xs' in fs.keys():
            for k, v in fs.get('xs').items():
                inline_styles[k] = v
        return inline_styles

    @classmethod
    def _compute_image_size(cls, image, dev_max_width, dev_img_fraction, given_fixed_size):

        def _compute_aspect_ratio(_image):
            if _image.exif.get('Orientation', 1) > 4:
                # image is rotated by 90 degrees, while keeping width and height
                return float(_image.width) / float(_image.height)
            else:
                return float(_image.height) / float(_image.width)

        def _clean_w(width):
            if width > dev_max_width:
                return dev_max_width
            return round(width)

        if not image:
            return

        aspect_ratio = _compute_aspect_ratio(image)
        fallback_width = round(dev_max_width * dev_img_fraction)

        g_w = given_fixed_size['width']
        g_h = given_fixed_size['height']

        gnp = SizeField.get_number_part
        if g_w and g_h:
            # fixed width **and** height given

            if 'px' in g_w and 'px' in g_h:
                # both are in px
                return _clean_w(gnp(g_w)), round(gnp(g_h))
            elif 'px' in g_w:
                # width in px
                return _clean_w(gnp(g_w)), 0
            elif 'px' in g_h:
                # height in px
                h = gnp(g_h)
                return round(h / aspect_ratio), round(h)
            else:
                # fallback dev_max_width * fraction
                return fallback_width, 0

        elif g_w:
            # fixed width given
            if 'px' in g_w:
                # width in px
                return _clean_w(gnp(g_w)), 0
            else:
                # fallback dev_max_width * fraction
                return fallback_width, 0

        elif g_h:
            # fixed height given
            if 'px' in g_h:
                # height in px
                h = gnp(g_h)
                return round(h / aspect_ratio), round(h)
            else:
                # fallback dev_max_width * fraction
                return fallback_width, 0
        else:
            # no fixed
            return fallback_width, 0

    @classmethod
    def _get_fixed_sizes(cls, instance):
        """
        get the img fixed_sizes for style scoped, e.g:

        fixed_sizes': {'xs': {'width': '100vw'}, 'md': {'width': '50vw'}}}

        """
        fixed_sizes = {}  # for scoped media depending on style

        fixed_size = {
            'width': instance.glossary.get('fixed_width_xs'), 'height':
                instance.glossary.get('fixed_height_xs')}

        for dev in cps.DEVICES:
            # inherits from xs or other value for higher device
            for attr in ['width', 'height']:
                k = 'fixed_%s_%s' % (attr, dev)
                v = instance.glossary.get(k)
                if v:
                    if not fixed_sizes.get(dev):
                        fixed_sizes[dev] = {}
                    fixed_sizes[dev][attr] = v
                    fixed_size[attr] = v
        return fixed_sizes

    @classmethod
    def _get_media_sizes(cls, instance):
        """
        creates media_queries (srcset - sizes), e.g:

        media_queries = {
          'xs': '(max-width: 575.98px) 575px',
          'sm': '(max-width: 767.98px) 767px',
          'md': '(max-width: 991.98px) 496px',
          'lg': '(max-width: 1199.98px) 600px',
          'xl': '800px'}

        and the img sizes for easythumbnail, e.g:

        easythumb_sizes = {
          'xs': (575, 0),
          'sm': (767, 0),
          ...
        }.
        """
        glossary = instance.glossary

        # img_dev_width_* contains '1/2' or '1/3' (of screen size)
        dev_img_fraction = eval(glossary.get('img_dev_width_xs'))
        fixed_size = {
            'width': glossary.get('fixed_width_xs'), 'height':
                glossary.get('fixed_height_xs')}

        queries = {}  # for srcset sizes
        ets = {}  # easythumb_sizes
        for dev in cps.DEVICES:

            # inherits from xs or other value for higher device
            _dev_img_fraction = glossary.get('img_dev_width_%s' % dev)
            if _dev_img_fraction:
                dev_img_fraction = eval(_dev_img_fraction)

            dev_max_w = cps.DEVICE_MAX_WIDTH_MAP.get(dev)
            ets[dev] = cls._compute_image_size(
                glossary.get('image_file'), dev_max_w,
                dev_img_fraction, fixed_size)

            if dev != 'xl':
                queries[dev] = '(max-width: %.2fpx) %.2fpx' % (dev_max_w, ets[dev][0])
            else:
                queries[dev] = '%.2fpx' % ets[dev][0]

        return queries, ets


# Background Image
# ----------------
#
class BackgroundImageForm(PlusPluginFormBase):

    image_file = PlusFilerImageSearchField(
        label=_('Background Image File'),
        required=True,
    )

    image_title = forms.CharField(
        label=_('Background Image Title'),
        required=False,
        help_text=_(
            'Caption text added to the "title" attribute of the '
            '<div> background image container element.'),
    )

    image_filter = forms.ChoiceField(
        label='Image Filter', required=False,
        choices=cps.BGIMG_FILTER_CHOICES, initial='',
        help_text='The color filter to be applied over the unhovered image.')

    do_thumbnail = forms.BooleanField(
        label=_('Do thumbnail'), initial=True, required=None,
        help_text=_('Scale (thumbnail) image according to given device sizes below.'))

    crop = forms.BooleanField(
        label=_('Crop'), initial=True, required=False,
        help_text=_('Cut image before scale to given device size.'))

    crop_spec = forms.CharField(
        label=_('Crop Specifiaction'), initial='', required=False,
        help_text=_('Specifiy cropping, e.g.: smart | scale | 0,10 | ,0) - leave empty for default behavior.'))

    upscale = forms.BooleanField(
        label=_('Upscale'), initial=False, required=False,
        help_text=_('Upscale image during scaling to given device size.'))

    # img_dev_width - fields are added below
    bottom_margin = forms.ChoiceField(
        label=u'Bottom Margin',
        required=False, choices=cps.CNT_BOTTOM_MARGIN_CHOICES,
        initial='',
        help_text='Select the default bottom margin to be applied?')

    STYLE_CHOICES = 'BACKGROUND_IMAGE_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)

    @classmethod
    def extend_form_fields(cls):
        for field_name, field in get_img_dev_width_fields():
            cls.declared_fields[field_name] = field


BackgroundImageForm.extend_form_fields()


class BackgroundImagePropertiesMixin():

    @staticmethod
    def eval_background_image_props(instance):
        # shorty
        igg = instance.glossary.get

        if not igg('do_thumbnail', False):
            return {}

        # scoped style background image widths
        bgimgwidths = {}
        ratio = igg('img_dev_width_xs') or '1/4'
        for dev in cps.DEVICES:
            width_key = 'img_dev_width_%s' % dev
            if igg(width_key):
                ratio = igg(width_key)
            k = cps.DEVICE_MIN_WIDTH_MAP.get(dev)
            w = cps.DEVICE_MAX_WIDTH_MAP.get(dev)
            # e.g. for md -> k=768, w=991, ratio=1/2: v = 991*1/2=496
            bgimgwidths[k] = '%dx0' % round(w * eval(ratio))

        if igg('crop', False) and igg('crop_spec', ''):
            crop = igg('crop_spec')  # smart or scale or 0,10 or ,10 ...
        else:
            crop = igg('crop')  # True or False

        return {
            'bgimgwidths': bgimgwidths,
            'crop': crop,  # boolean or str
        }


class BackgroundImagePlugin(BackgroundImagePropertiesMixin, BootstrapPluginBase):
    footnote_html = """
        Renders a div container with a background image.
        <br>
        if a filter is given, the image is put in the containers after tag, and placed below the filter.
    """
    name = _("Background Img")
    allow_children = True
    form = BackgroundImageForm
    render_template = 'cmsplus/bootstrap/background-image/background-image.html'

    tag_attr_map = {'image_title': 'title'}
    css_class_fields = StylePluginMixin.css_class_fields + ['bottom_margin']

    fieldsets = [
        (None, {
            'fields': (
                'image_file', 'image_title',
                'image_filter', 'bottom_margin'),
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

        (_('Responsive options'), {
            'classes': ('collapse',),
            'description': _(
                'Maximum responsive width per device used to '
                'provide optimal image size for each device with respect to '
                'loading time.'),
            'fields': (
                'do_thumbnail',
                ('crop', 'crop_spec', 'upscale'),
                [field_name for field_name, field in get_img_dev_width_fields()],
            ),
        }),

    ]

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context.update(self.eval_background_image_props(instance))
        return context


# HeadingPlugin
# -------------
#
class HeadingForm(PlusPluginFormBase):
    TAG_TYPES = [('h{}'.format(k), _("Heading {}").format(k)) for k in range(1, 7)]

    tag_type = forms.ChoiceField(
        choices=TAG_TYPES,
        label=_("HTML element tag"),
        help_text=_('Choose a tag type for this HTML element.')
    )

    content = forms.CharField(
        label=_("Heading content"),
        widget=forms.widgets.TextInput(
            attrs={'style': 'width: 100%; padding-right: 0; font-weight: bold; font-size: 125%;'}),
    )

    background_color = forms.ChoiceField(
        choices=cps.BG_COLOR_CHOICES,
        label=_("Background Color"),
        required=False,
        help_text=_('Select a background color.')
    )

    bottom_margin = forms.ChoiceField(
        label=u'Bottom Margin',
        required=False, choices=cps.CNT_BOTTOM_MARGIN_CHOICES,
        initial='',
        help_text='Select the default bottom margin to be applied?')

    element_id = forms.CharField(label=_('Element ID'), max_length=255, required=False)

    STYLE_CHOICES = 'HEADING_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class HeadingPlugin(BootstrapPluginBase):
    footnote_html = """
        Renders a bootstrap heading (h1-h6) with the ability to display a background box.
    """
    name = _("Heading")
    parent_classes = None
    allow_children = False
    form = HeadingForm
    render_template = 'cmsplus/bootstrap/heading.html'

    @classmethod
    def get_identifier(cls, instance):
        tag_type = instance.glossary.get('tag_type')
        content = mark_safe(instance.glossary.get('content', ''))
        if tag_type:
            return format_html('<code>{0}</code>: {1}', tag_type, content)
        return content

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context.update({'content': mark_safe(instance.glossary.get('content', ''))})
        return context


# Figure Plugin
# -------------
#
class FigureForm(PlusPluginFormBase):

    caption = forms.CharField(
        label=_("Figure Caption"),
        widget=forms.widgets.TextInput(attrs={'style': 'width: 100%; padding-right: 0;'}),
    )

    STYLE_CHOICES = 'FIGURE_CAPTION_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapFigurePlugin(BootstrapPluginBase):
    footnote_html = """
    Renders a bootstrap figure plugin to display a figure caption.
    """
    name = _("Figure")
    parent_classes = None
    allow_children = True
    form = FigureForm
    render_template = 'cmsplus/bootstrap/figure.html'
    default_css_class = 'figure-caption'


# Embed Plugin
# ------------
#
class EmbedForm(PlusPluginFormBase):

    url = forms.URLField(
        label=_("Media URL"),
        widget=widgets.URLInput(attrs={'size': 50}),
        help_text=_(
            'Video Url to an external service w/o query params such as YouTube, Vimeo or others, ' 'e.g.: '
            'https://www.youtube.com/embed/vZw35VUBdzo'),
    )

    ASPECT_RATIO_CHOICES = [
        ('embed-responsive-21by9', _("Responsive 21:9")),
        ('embed-responsive-16by9', _("Responsive 16:9")),
        ('embed-responsive-4by3', _("Responsive 4:3")),
        ('embed-responsive-1by1', _("Responsive 1:1")),
    ]
    aspect_ratio = forms.ChoiceField(
        label=_("Aspect Ratio"),
        choices=ASPECT_RATIO_CHOICES,
        widget=widgets.RadioSelect,
        required=False,
        initial=ASPECT_RATIO_CHOICES[1][0],
    )

    allow_fullscreen = forms.BooleanField(
        label=_("Allow Fullscreen"),
        required=False,
        initial=True,
    )

    autoplay = forms.BooleanField(
        label=_("Autoplay"),
        required=False,
    )

    controls = forms.BooleanField(
        label=_("Display Controls"),
        required=False,
    )

    loop = forms.BooleanField(
        label=_("Enable Looping"),
        required=False,
        help_text=_('Inifinte loop playing.'),
    )

    rel = forms.BooleanField(
        label=_("Show related"),
        required=False,
        help_text=_('Show related media content'),
    )

    STYLE_CHOICES = 'EMBED_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapEmbedPlugin(BootstrapPluginBase):
    footnote_html = """
        Renders a bootstrap embed iframe for playing (e.g. youtube) videos.
        <br>
        It can be used with a modal popup or direct.
    """
    name = _("Embed Video")
    allow_children = False
    form = EmbedForm
    render_template = 'cmsplus/bootstrap/embed.html'
    default_css_class = 'embed-responsive'
    css_class_fields = StylePluginMixin.css_class_fields + ['aspect_ratio']

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        url = instance.glossary.get('url')
        params = {}
        for k in ['autoplay', 'controls', 'loop', 'rel']:
            if instance.glossary.get(k):
                params[k] = instance.glossary.get(k)

        q = urllib.parse.urlencode(params)
        context.update({
            'embed_url': '%s?%s' % (url, q),
            'allowfullscreen': 'allowfullscreen' if instance.glossary.get('allow_fullscreen') else '',
        })
        return context


# Button Plugin
# -------------
#
class BootstrapButtonForm(LinkFormBase):
    content = forms.CharField(label=_('Content'), required=False,
            help_text='Button content, e.g.: Click me, or nothing for icon only button')

    BUTTON_SIZES = [
        ('btn-lg', _("Large button")),
        ('', _("Default button")),
        ('btn-sm', _("Small button")),
    ]

    button_size = forms.ChoiceField(
        label=_("Button Size"),
        choices=BUTTON_SIZES,
        initial='',
        required=False,
        help_text=_("Button Size to use.")
    )

    button_block = forms.ChoiceField(
        label=_("Button Block"),
        choices=[
            ('', _('No')),
            ('btn-block', _('Block level button')),
        ],
        required=False,
        initial='',
        help_text=_("Use button block option (span left to right)?")
    )

    icon_position = forms.ChoiceField(
        label=_("Icon position"),
        choices=[
            ('icon-top', _("Icon top")),
            ('icon-right', _("Icon right")),
            ('icon-left', _("Icon left")),
        ],
        initial='icon-right',
        help_text=_("Select icon position related to content."),
    )

    icon = IconField(required=False)

    STYLE_CHOICES = 'BOOTSTRAP_BUTTON_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class BootstrapButtonPluginModel(PlusPlugin, LinkPluginMixin):
    class Meta:
        proxy = True


class BootstrapButtonPlugin(StylePluginMixin, LinkPluginBase):
    footnote_html = """
        renders a bootstrap button with various styles. The button may trigger a
        internal or external page link, a download oder mailto link.
    """
    module = 'Bootstrap'
    name = _('Button')
    parent_classes = None
    require_parent = False
    allow_children = False
    default_css_class = 'btn'
    render_template = 'cmsplus/bootstrap/button.html'

    form = BootstrapButtonForm
    model = BootstrapButtonPluginModel

    css_class_fields = StylePluginMixin.css_class_fields + ['button_size', 'button_block']

    class Media:
        css = {'all': ['cmsplus/admin/icon_plugin/css/icon_plugin.css'] + get_icon_style_paths()}
        js = ['cmsplus/admin/icon_plugin/js/icon_plugin.js']

    fieldsets = [
        (None, {
            'fields': ('content', ),
        }),
        (_('Styles'), {
            'fields': (
                ('extra_style', 'button_size', 'button_block'),
            ),
        }),
        (_('Link settings'), {
            'fields': (
                'link_type', 'cms_page', 'section', 'download_file', 'file_as_page', 'ext_url',
                'mail_to', 'link_target', 'link_title'
            )
        }),
        (_('Icon settings'), {
            'classes': ('collapse',),
            'fields': (
                'icon_position', 'icon',
            )
        }),
        (_('Extra settings'), {
            'classes': ('collapse',),
            'fields': (
                'extra_classes',
                'label',
            )
        }),
    ]

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        icon_pos = instance.glossary.get('icon_position')
        icon = instance.glossary.get('icon')

        if icon:
            if icon_pos == 'icon-top':
                context['icon_top'] = format_html('&nbsp; <i class="{}"></i><br>'.format(icon))
            elif icon_pos == 'icon-left':
                context['icon_left'] = format_html('&nbsp; <i class="{}"></i>'.format(icon))
            elif icon_pos == 'icon-right':
                context['icon_right'] = format_html('&nbsp; <i class="{}"></i>'.format(icon))

        return context

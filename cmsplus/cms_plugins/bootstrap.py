from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cmsplus.app_settings import cmsplus_settings as cps
from cmsplus.fields import SizeField
from cmsplus.forms import (PlusPluginFormBase, LinkFormBase,
                           get_style_form_fields, get_image_form_fields)
from cmsplus.models import PlusPlugin, LinkPluginMixin
from cmsplus.plugin_base import (PlusPluginBase, StylePluginMixin,
                                 LinkPluginBase)


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

    STYLE_CHOICES = 'MAGIC_WRAPPER_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            'fields': [WF_MARGIN_KEYS(for_dev=[dev]) for dev in cps.DEVICES],
        }),

        (_('Padding settings'), {
            'classes': ('collapse',),
            'fields': [WF_PADDING_KEYS(for_dev=[dev]) for dev in cps.DEVICES],
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
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)


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
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)


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
            choices = [('', 'flex'), ]
        else:
            choices = [('', 'inherit'), ]
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
            choices = [('', 'none'), ]
        else:
            choices = [('', 'inherit'), ]
        choices.extend(self.get_attr_choices(tok, 'offset'))
        return choices

    def col_order_choices(self, dev):
        '''
        return tuples of ('order-md-1', 'order 1')
        '''
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
        '''
        return tuples of ('d-*-block', 'd-block')
        '''
        DISPLAY_VALUES = ['block', 'flex', 'inline', 'inline-block', 'none', 'table', 'table-cell']
        tok = self.get_dev_token(dev)
        if dev == 'xs':
            choices = [('', 'not set'), ]
        else:
            choices = [('', 'inherit'), ]

        for v in DISPLAY_VALUES:
            choices.append(('d%s-%s' % (tok, v), '%s' % v),)
        return choices

    def get_column_form_fields(self, attrs=[], initials={}, choices={}):
        _attrs = attrs or ['offset', 'width', 'order', 'display']

        for attr in _attrs:
            for dev in cps.DEVICES:
                field_name = 'col_%s_%s' % (attr, dev)

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
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

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
        ColDefHelper(col_range=13, col_base=''))  # default 12 divided form

MCF_COLUMN_KEYS = BootstrapColumnForm.get_column_keys


class BootstrapColPlugin(BootstrapPluginBase):
    footnote_html = """
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
    ]


# 10 divided column form and plugin
# ---------------------------------
class BootstrapCol10Form(BootstrapColumnForm):
    ''' 10 divided column form.
    '''


BootstrapCol10Form._extend_form_fields(
        ColDefHelper(col_range=11, col_base='10'))


class BootstrapCol10Plugin(BootstrapColPlugin):
    footnote_html = """
    renders a bootstrap 10 divided column with variable offset and with.
    """
    name = _('Column 1/10')
    form = BootstrapCol10Form


# Image Plugin
# ------------
#
def get_img_dev_width_fields(initials={}):
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

    image_file, image_title, image_alt = get_image_form_fields()

    STYLE_CHOICES = 'IMAGE_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

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
        help_text=_("How to align the image."),
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
        help_text=_("Options to use when resizing the image."),
        initial=['crop'],
    )
    # img_dev_width fields are added with _extend_form_fields below

    @classmethod
    def _extend_form_fields(cls):
        for field_name, field in get_fixed_dim_fields('width'):
            cls.declared_fields[field_name] = field
        for field_name, field in get_fixed_dim_fields('height'):
            cls.declared_fields[field_name] = field
        for field_name, field in get_img_dev_width_fields():
            cls.declared_fields[field_name] = field


BootstrapImageForm._extend_form_fields()


class BootstrapImagePluginModel(PlusPlugin, LinkPluginMixin):
    class Meta:
        proxy = True


class BootstrapImagePlugin(StylePluginMixin, LinkPluginBase):
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

    # ring_plugin = 'ImagePlugin'
    # class Media:
    #    js = ['admin/js/jquery.init.js', 'cascadex/admin/imageplugin.js']

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
                ('fixed_width_xs', 'fixed_width_sm', 'fixed_width_md', 'fixed_width_lg', 'fixed_width_xl',),
                ('fixed_height_xs', 'fixed_height_sm', 'fixed_height_md', 'fixed_height_lg', 'fixed_height_xl',),
            ),
        }),
        (_('Responsive options'), {
          'classes': ('collapse',),
          'description': _(
              'Maximum responsive width per device if no fixed '
              '(px) width or height given. Used to provide optimal image size '
              'for each device with respect to loading time.'),
          'fields': (
               ('img_dev_width_xs', 'img_dev_width_sm', 'img_dev_width_md',
                   'img_dev_width_lg', 'img_dev_width_xl',),
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
                'link_type', 'cms_page', 'section', 'download_file', 'ext_url',
                'mail_to', 'link_target', 'link_title'
            )
        }),
    ]

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        glossary = instance.glossary
        media_queries, easy_thumb_sizes = self._get_media_sizes(
                instance)

        # srcset sizes
        context['sizes'] = [media_queries[dev] for dev in cps.DEVICES]

        # srcset
        srcset = {}
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

        def _compute_aspect_ratio(image):
            if image.exif.get('Orientation', 1) > 4:
                # image is rotated by 90 degrees, while keeping width and height
                return float(image.width) / float(image.height)
            else:
                return float(image.height) / float(image.width)

        def _clean_w(width):
            if width > dev_max_width:
                return dev_max_width
            return round(width)

        aspect_ratio = _compute_aspect_ratio(image)
        fallback_width = round(dev_max_width * dev_img_fraction)

        g_w = given_fixed_size['width']
        g_h = given_fixed_size['height']

        gnp = SizeField.get_number_part
        if g_w and g_h:
            # fixed width **and** height given

            if 'px' in g_w and 'px' in g_h:
                # both are in px
                return (_clean_w(gnp(g_w)), round(gnp(g_h)))
            elif 'px' in g_w:
                # width in px
                return (_clean_w(gnp(g_w)), 0)
            elif 'px' in g_h:
                # height in px
                h = gnp(g_h)
                return (round(h/aspect_ratio), round(h))
            else:
                # fallback dev_max_width * fraction
                return (fallback_width, 0)

        elif g_w:
            # fixed width given
            if 'px' in g_w:
                # width in px
                return (_clean_w(gnp(g_w)), 0)
            else:
                # fallback dev_max_width * fraction
                return (fallback_width, 0)

        elif g_h:
            # fixed height given
            if 'px' in g_h:
                # height in px
                h = gnp(g_h)
                return (round(h/aspect_ratio), round(h))
            else:
                # fallback dev_max_width * fraction
                return (fallback_width, 0)
        else:
            # no fixed
            return (fallback_width, 0)

    @classmethod
    def _get_fixed_sizes(cls, instance):
        """
        get the img fixed_sizes for style scoped, e.g:

        fixed_sizes': {'xs': {'width': '100vw'}, 'md': {'width': '50vw'}}}

        """
        fixed_sizes = {}  # for scoped media depending style

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
        }
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

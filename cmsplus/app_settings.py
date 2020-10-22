from django.conf import settings

from cmsplus.utils import JSONEncoder

DEFAULTS = {
    'PLUGINS': (
        'cmsplus.cms_plugins.generic.MultiColumnTextPlugin',
        'cmsplus.cms_plugins.generic.SnippetPlugin',
        'cmsplus.cms_plugins.generic.TextLinkPlugin',
        'cmsplus.cms_plugins.generic.SvgImagePlugin',
        'cmsplus.cms_plugins.generic.VerticalRatioSpacerPlugin',
        'cmsplus.cms_plugins.generic.BackgroundVideoPlugin',
        'cmsplus.cms_plugins.generic.slider.SlidePlugin',
        'cmsplus.cms_plugins.generic.slider.SliderPlugin',
        'cmsplus.cms_plugins.generic.icon.IconPlugin',
        'cmsplus.cms_plugins.generic.AudioEmbedPlugin',

        'cmsplus.cms_plugins.osm.OsmPlugin',
        'cmsplus.cms_plugins.osm.OsmMarkerPlugin',

        'cmsplus.cms_plugins.bootstrap.MagicWrapperPlugin',
        'cmsplus.cms_plugins.bootstrap.BootstrapContainerPlugin',
        'cmsplus.cms_plugins.bootstrap.BootstrapRowPlugin',
        'cmsplus.cms_plugins.bootstrap.BootstrapColPlugin',
        'cmsplus.cms_plugins.bootstrap.BootstrapImagePlugin',
        'cmsplus.cms_plugins.bootstrap.BackgroundImagePlugin',
        'cmsplus.cms_plugins.bootstrap.HeadingPlugin',
        'cmsplus.cms_plugins.bootstrap.BootstrapFigurePlugin',
        'cmsplus.cms_plugins.bootstrap.BootstrapEmbedPlugin',
        'cmsplus.cms_plugins.bootstrap.BootstrapButtonPlugin',
        'cmsplus.cms_plugins.bootstrap.accordion.BootstrapAccordionPlugin',
        'cmsplus.cms_plugins.bootstrap.accordion.BootstrapAccordionGroupPlugin',
        'cmsplus.cms_plugins.bootstrap.card.BootstrapCardHeaderPlugin',
        'cmsplus.cms_plugins.bootstrap.card.BootstrapCardBodyPlugin',
        'cmsplus.cms_plugins.bootstrap.card.BootstrapCardFooterPlugin',
        'cmsplus.cms_plugins.bootstrap.card.BootstrapCardPlugin',
    ),

    'JSON_ENCODER_CLASS': JSONEncoder,

    'MAP_LAYER_CHOICES': (
        ('', 'None'),
        ('stamen', 'Stamen'),
        ('black', 'Black'),
    ),

    'DEVICES': ('xs', 'sm', 'md', 'lg', 'xl'),
    'DEVICE_MAP': {'xs': 'phone', 'sm': 'tablet sm', 'md': 'tablet', 'lg': 'desktop', 'xl': 'desktop xl', },
    'DEVICE_MAX_WIDTH_MAP': {'xs': 575, 'sm': 767, 'md': 991, 'lg': 1199, 'xl': 1599, },
    'DEVICE_MIN_WIDTH_MAP': {'xs': 0, 'sm': 576, 'md': 768, 'lg': 992, 'xl': 1200, },

    'TEXT_COLOR_CHOICES': (
        ('', 'Default'),
        ('text-primary', 'Primary'),
        ('text-secondary', 'Secondary'),
        ('text-light', 'Light'),
        ('text-dark', 'Dark'),
        ('text-info', 'Info'),
        ('text-success', 'Success'),
        ('text-warning', 'Warning'),
        ('text-danger', 'Danger'),
    ),
    'BG_COLOR_CHOICES': (
        ('', 'Transparent'),
        ('bg-primary', 'Primary'),
        ('bg-secondary', 'Secondary'),
        ('bg-light', 'Light'),
        ('bg-dark', 'Dark'),
        ('bg-info', 'Info'),
        ('bg-success', 'Success'),
        ('bg-warning', 'Warning'),
        ('bg-danger', 'Danger'),
    ),
    'RL_MARGIN_CHOICES': (
        ('1cw', '1 Col'),
        ('160', '10 Unit (160)'),
        ('120', '7.5 Unit (120)'),
        ('80', '5 Unit (80)'),
        ('64', '4 Unit (64)'),
        ('48', '3 Unit (48)'),
        ('40', '2.5 Unit'),
        ('32', '2 Unit (32)'),
        ('30', 'gutter (30)'),
        ('24', '1.5 Unit (24)'),
        ('16', '1 Unit (16)'),
        ('15', '1/2 gutter (15)'),
        ('8', '.5 Unit (8)'),
        ('4', '.25 Unit (4)'),
        ('0', '0'),
        ('-4', '-.25 Unit (4)'),
        ('-8', '-.5 Unit (8)'),
        ('bleed', 'Bleed (-15)'),
        ('-16', '-1 Unit (16)'),
        ('-24', '-1.5 Unit (24)'),
        ('-32', '-2 Unit (32)'),
        ('-40', '-2.5 Unit (40)'),
        ('-48', '-5 Unit (80)'),
        ('-64', '-4 Unit (64)'),
        ('-80', '-5 Unit (80)'),
        ('-120', '-7.5 Unit (120)'),
        ('-160', '-10 Unit (160)'),
        ('-1cw', '-1 Col'),
    ),
    'TB_MARGIN_CHOICES': (
        ('160', '10 Unit (160)'),
        ('120', '7.5 Unit (120)'),
        ('80', '5 Unit (80)'),
        ('64', '4 Unit (64)'),
        ('48', '3 Unit (48)'),
        ('40', '2.5 Unit'),
        ('24', '1.5 Unit (24)'),
        ('32', '2 Unit (32)'),
        ('16', '1 Unit (16)'),
        ('8', '.5 Unit (8)'),
        ('4', '.25 Unit (4)'),
        ('0', '0'),
        ('-4', '-.25 Unit (4)'),
        ('-8', '-.5 Unit (8)'),
        ('-16', '-1 Unit (16)'),
        ('-24', '-1.5 Unit (24)'),
        ('-32', '-2 Unit (32)'),
        ('-40', '-2.5 Unit (40)'),
        ('-48', '-5 Unit (80)'),
        ('-64', '-4 Unit (64)'),
        ('-80', '-5 Unit (80)'),
        ('-120', '-7.5 Unit (120)'),
        ('-160', '-10 Unit (160)'),
    ),
    'PADDING_CHOICES': (
        ('160', '10 Unit (160)'),
        ('120', '7.5 Unit (120)'),
        ('80', '5 Unit (80)'),
        ('64', '4 Unit (64)'),
        ('48', '3 Unit (48)'),
        ('40', '2.5 Unit'),
        ('32', '2 Unit (32)'),
        ('30', 'gutter (30)'),
        ('24', '1.5 Unit (24)'),
        ('16', '1 Unit (16)'),
        ('15', '1/2 gutter (15)'),
        ('8', '.5 Unit (8)'),
        ('4', '.25 Unit (4)'),
        ('0', '0'),
    ),

    'CNT_BOTTOM_MARGIN_CHOICES': (
        ('mb-3 mb-md-5', 'Default'),
        ('mb-2 mb-md-3', 'Small'),
        ('', 'None'),
    ),
    'ROW_BOTTOM_MARGIN_CHOICES': (
        ('', 'None'),
        ('mb-3 mb-md-5', 'Default'),
        ('mb-2 mb-md-3', 'Small'),
    ),
    'COL_BOTTOM_MARGIN_CHOICES': (
        ('mb-3 mb-md-5', 'Default'),
        ('mb-2 mb-md-3', 'Small'),
        ('', 'None'),
    ),

    'TX_COL_CHOICES': (
        ('2', '2 Text Columns'),
        ('3', '3 Text Columns'),
        # remember to inc col no in scss
    ),

    'IMG_DEV_WIDTH_CHOICES': (
        ('1', 'full screen'),
        ('3/4', '3/4 screen'),
        ('2/3', '2/3 screen'),
        ('1/2', '1/2 screen'),
        ('1/3', '1/3 screen'),
        ('1/4', '1/4 screen'),
        ('1/5', '1/5 screen'),
        ('1/6', '1/6 screen'),
    ),

    'BGIMG_FILTER_CHOICES': (
        ('', 'None'),
    ),

    'ICONS_FONTAWESOME': {
        'meta': 'cmsplus/icons/fontawesome/metadata/icons.json',
        'css': 'cmsplus/icons/fontawesome/css/all.css',
    },
    # show and hide icons in project
    'ICONS_FONTAWESOME_SHOW': True,

    # custom fontello font packs
    'ICONS_FONTELLO': [
        # { 'meta': '', 'css': '' }
    ],

    'MAGIC_WRAPPER_STYLES': (
        ('', 'None'),
    ),

    'MOD_CONTAINER_STYLES': (
        ('', 'None'),
    ),

    'MOD_ROW_STYLES': (
        ('', 'None'),
    ),

    'MOD_COL_STYLES': (
        ('', 'None'),
    ),

    'IMAGE_STYLES': (
        ('', 'None'),
    ),

    'BACKGROUND_IMAGE_STYLES': (
        ('', 'None'),
    ),

    'CARD_STYLES': (
        ('', 'Default'),
    ),
    'CARD_HEADER_STYLES': (
        ('', 'Default'),
    ),
    'CARD_BODY_STYLES': (
        ('', 'Default'),
    ),
    'CARD_FOOTER_STYLES': (
        ('', 'Default'),
    ),
}


class CmsPlusSettings:

    def __init__(self, site_settings=None, defaults=None):
        self.site_settings = site_settings
        self.defaults = defaults

    def __getattr__(self, attr):
        ret = self.site_settings.get(attr, self.defaults.get(attr))
        if ret is None and attr not in self.site_settings and attr not in self.defaults:
            raise AttributeError
        return ret

    def get_all(self):
        return [(k, getattr(self, k)) for k in self.defaults.keys()]


cmsplus_settings = CmsPlusSettings(getattr(settings, 'CMSPLUS', {}), DEFAULTS)

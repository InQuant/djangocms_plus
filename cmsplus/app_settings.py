from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class DefaultSettings(object):
    
    def settings(self):
        return {
            'PLUGINS': (
                'cmsplus.cms_plugins.generic.TextLinkPlugin',

                'cmsplus.cms_plugins.osm.OsmPlugin',
                'cmsplus.cms_plugins.osm.OsmMarkerPlugin',

                'cmsplus.cms_plugins.bootstrap.MagicWrapperPlugin',
                'cmsplus.cms_plugins.bootstrap.BootstrapContainerPlugin',
            ),

            'MAP_LAYER_CHOICES': (
                ('', 'None'),
                ('black', 'Black'),
            ),

            'DEVICES' : ('xs', 'sm', 'md', 'lg', 'xl'),
            'DEVICE_MAP' : {'xs': 'phone', 'sm': 'tablet sm', 'md': 'tablet', 'lg':
                'desktop', 'xl': 'desktop xl'},
            'DEVICE_MAX_WIDTH_MAP' : {
                'xs': 575,
                'sm': 767,
                'md': 991,
                'lg': 1199,
                'xl': 1599,
            },
            'DEVICE_MIN_WIDTH_MAP' : {
                'xs': 0,
                'sm': 576,
                'md': 768,
                'lg': 992,
                'xl': 1200,
            },

            'TEXT_COLOR_CHOICES' : (
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
            'BG_COLOR_CHOICES' : (
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
            'RL_MARGIN_CHOICES' : (
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
            'TB_MARGIN_CHOICES' : (
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
            'PADDING_CHOICES' : (
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

            'CNT_BOTTOM_MARGIN_CHOICES' : (
                ('mb-3 mb-md-5', 'Default'),
                ('mb-2 mb-md-3', 'Small'),
                ('', 'None'),
            ),
        }

# Overwrite DefaultSettings, with those, configured in site settings
app_settings = DefaultSettings().settings()
app_settings.update(getattr(settings, 'CMSPLUS_SETTINGS', {}).items())

# make them global for this module
globals().update(app_settings.items())

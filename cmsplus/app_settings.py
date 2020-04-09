from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class DefaultSettings(object):
    
    def settings(self):
        return {
            'PLUGINS': (
                'cmsplus.cms_plugins.generic.TextLinkPlugin',
            ),
        }

# Overwrite DefaultSettings, with those, configured in site settings
app_settings = DefaultSettings().settings()
app_settings.update(getattr(settings, 'CMSPLUS_SETTINGS', {}).items())

# make them global for this module
globals().update(app_settings.items())

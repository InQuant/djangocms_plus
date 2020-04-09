from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
import logging
logger = logging.getLogger(__name__)


class DjangoCmsPlusConfig(AppConfig):
    name = 'cmsplus'
    verbose_name = _('DjangoCMS Plus')

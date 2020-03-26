from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
import logging
logger = logging.getLogger(__name__)


class DjangocmsPlusConfig(AppConfig):
    name = 'djangocms_plus'
    verbose_name = _('DjangoCMS Plus')
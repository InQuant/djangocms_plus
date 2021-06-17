import logging

from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q

from cmsplus.app_settings import cmsplus_settings
from cmsplus.models import SiteStyle, scss_storage

logger = logging.getLogger('django')


def font_assets(request):
    css = []
    js = []

    if cmsplus_settings.ICONS_FONTAWESOME_SHOW:
        _css = cmsplus_settings.ICONS_FONTAWESOME.get('css')
        _js = cmsplus_settings.ICONS_FONTAWESOME.get('js')

        css.append(_css) if _css else None
        js.append(_js) if _js else None

    for f in getattr(cmsplus_settings, 'ICONS_FONTELLO', []):
        css.append(f.get('css')) if f.get('css') else None
        js.append(f.get('js')) if f.get('js') else None

    return {
        'CMSPLUS_FONT_CSS': css,
        'CMSPLUS_FONT_JS': js,
    }


def site_styles(request):
    styles = SiteStyle.objects.filter(Q(site__isnull=True) | Q(site=get_current_site(request))).order_by('order')
    r = []
    for style in styles:
        if not scss_storage.exists(style.file.name):
            logger.error(f'{style} does not exist!')
            continue
        r.append(r)

    return {'SITE_STYLES': r}

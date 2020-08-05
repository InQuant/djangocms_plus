from cmsplus.app_settings import cmsplus_settings


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

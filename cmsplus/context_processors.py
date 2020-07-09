from cmsplus.app_settings import cmsplus_settings


def font_assets(request):
    css = []
    js = []

    for icon_dir_str in cmsplus_settings.ICONS_DIR:
        icon_dir = cmsplus_settings.ICONS_DIR[icon_dir_str]
        css.append(icon_dir.get('css')) if icon_dir.get('css') else None
        css.append(icon_dir.get('js')) if icon_dir.get('js') else None

    return {
        'CMSPLUS_FONT_CSS': css,
        'CMSPLUS_FONT_JS': js,
    }
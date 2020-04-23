import json
import os

from django import forms
from django.contrib.staticfiles import finders
from django.core.exceptions import ImproperlyConfigured
from django.forms.renderers import get_default_renderer
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cmsplus.app_settings import cmsplus_settings as cps
from cmsplus.forms import PlusPluginFormBase, get_style_form_fields
from cmsplus.plugin_base import PlusPluginBase


class IconFieldWidget(forms.Widget):
    template_name = "cmsplus/forms/widgets/icon.html"
    icons = []

    def __init__(self, attrs=None):
        super().__init__(attrs)
        # add fontawesome icons
        self.icons += self.get_fontawesome_icons

    def render(self, name, value, add_to_class=None, attrs=None, renderer=None):
        if renderer is None:
            renderer = get_default_renderer()

        context = self.get_context(name, value, attrs)
        context['widget']['icons'] = IconFieldWidget.icons
        context['widget']['value'] = value
        context['widget']['name'] = name
        context['widget']['attrs'] = attrs
        context['widget']['add_to_class'] = add_to_class
        return mark_safe(renderer.render(self.template_name, context))

    @cached_property
    def get_fontawesome_icons(self):
        icons = []
        # list of dicts:
        # { 'name': '',
        #   'label': '',
        #   'font_class_name': '', }

        path = finders.find(cps.ICONS_DIR['FONTAWESOME']['meta'])
        if not os.path.exists(path):
            raise ImproperlyConfigured('ICONS_DIR: FONTAWESOME: meta path is not existing (%s)' % path)

        with open(path, 'rb') as f:
            raw_data = f.read()
        try:
            data = json.loads(raw_data)
        except TypeError:
            # Python 3.5 compatibility
            data = json.loads(raw_data.decode('utf-8'))

        for key, value in data.items():
            # check styles ['brands', 'solid', 'regular']
            for style in value.get('styles'):
                if style == "solid":
                    font_class_name = "fas fa-%s" % key
                elif style == "brands":
                    font_class_name = "fab fa-%s" % key
                elif style == "regular":
                    font_class_name = "far fa-%s" % key
                else:
                    raise ValueError("%s style not defined" % style)

                icons.append({
                    'name': key,
                    'label': value.get('label'),
                    'font_class_name': font_class_name,
                })
        return icons

    # TODO: fontello implementieren


class IconField(forms.CharField):
    widget = IconFieldWidget


class IconFormPlugin(PlusPluginFormBase):
    STYLE_CHOICES = 'MOD_ICON_STYLES'
    extra_style, extra_classes, label = get_style_form_fields(STYLE_CHOICES)

    icon = IconField()


def get_icon_style_paths():
    fontawesome_path = cps.ICONS_DIR['FONTAWESOME']['css']
    return [fontawesome_path, ]


class IconPlugin(PlusPluginBase):
    footnote_html = """
    Choose icon from font defined in the settings
    """
    name = _('Icon')
    form = IconFormPlugin
    render_template = "cmsplus/generic/icon.html"
    allow_children = False
    text_enabled = True

    def render(self, context, instance, placeholder):
        context['css_styles'] = get_icon_style_paths()
        return super().render(context, instance, placeholder)

    class Media:
        css = {'all': ['cmsplus/admin/icon_plugin/css/icon_plugin.css'] + get_icon_style_paths()}
        js = ['cmsplus/admin/icon_plugin/js/icon_plugin.js']

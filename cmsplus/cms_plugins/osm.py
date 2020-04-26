from django import forms
from django.utils.translation import ugettext_lazy as _

from cmsplus.app_settings import cmsplus_settings as cps
from cmsplus.fields import PlusFilerFileSearchField
from cmsplus.forms import (PlusPluginFormBase, get_style_form_fields)
from cmsplus.models import PlusPlugin
from cmsplus.plugin_base import (PlusPluginBase, StylePluginMixin)


# Openstreetmap forms
# -------------------
#
class OsmForm(PlusPluginFormBase):
    latitude = forms.FloatField(
        label=_('Center Latitude'), required=True, help_text='Map center latitude, e.g. 47.798740')
    longitude = forms.FloatField(
        label=_('Center Longitude'), required=True, help_text='Map center longitude, e.g. 9.621890')
    zoom = forms.IntegerField(
        label=_('Zoom'), required=True, initial=15, help_text='Maps initial zoom.')
    map_height = forms.CharField(
        label=_('Height'), required=True, initial='30vh', help_text='Height of Map in px or rem or vh.')
    scroll_wheel_zoom = forms.BooleanField(
        label=_('Scroll Wheel Zoom'), required=False, initial=True, help_text='Map zoom via mouse scroll wheel?')

    layer = forms.ChoiceField(
        label=_('Custom Layer'),
        required=False,
        initial='',
        choices=cps.MAP_LAYER_CHOICES,
        help_text=_('Adds a custom (colored) layer to the map.'),
    )

    STYLE_CHOICES = 'OSM_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class OsmMarkerForm(PlusPluginFormBase):
    latitude = forms.FloatField(
        label=_('Latitude'), required=True, help_text='Latitude coordiante of the marker, e.g. 47.798740')
    longitude = forms.FloatField(
        label=_('Longitude'), required=True, help_text='Longitude coordinate of the marker, e.g. 9.621890')

    # it's a File to allow svg
    image_file = PlusFilerFileSearchField(
        label='Marker Image File',
        required=True,
    )


# Openstreetmap plugins
# ---------------------
#
class OsmPlugin(StylePluginMixin, PlusPluginBase):
    footnote_html = """
       renders a open streetmap with location.
       """
    name = _('OpenstreetMap')
    module = 'OpenStreetMap'
    form = OsmForm
    render_template = "cmsplus/osm/osm.html"
    child_classes = ['OsmMarkerPlugin', ]
    allow_children = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context['scroll_wheel_zoom_int'] = int(instance.glossary.get('scroll_wheel_zoom'))
        context['markers'] = [p.get_plugin_instance()[0] for p in instance.child_plugin_instances]
        return context


class OsmMarkerModel(PlusPlugin):
    class Meta:
        proxy = True

    @property
    def marker_url(self):
        return self.plugin_class.get_marker_url(self)

    @property
    def marker_name(self):
        return 'm%s' % self.id


class OsmMarkerPlugin(StylePluginMixin, PlusPluginBase):
    footnote_html = """
       renders a open streetmap marker on a map.
       """
    name = _('OsmMarker')
    module = 'OpenStreetMap'
    form = OsmMarkerForm
    model = OsmMarkerModel
    render_template = "cmsplus/osm/osm_marker.html"
    parent_classes = ['OsmPlugin', ]
    require_parent = True

    @classmethod
    def get_marker_url(cls, instance):
        img = instance.glossary.get('image_file')
        if img:
            return img.url
        return None

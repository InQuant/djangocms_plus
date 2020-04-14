from cms.models import CMSPlugin
from django.utils.functional import cached_property
from django.utils.html import mark_safe, format_html_join
from jsonfield import JSONField

from cmsplus.utils import JSONEncoder


class PlusPlugin(CMSPlugin):
    """
    BaseModel for plugins including the important json field.
    """
    _json = JSONField(encoder_class=JSONEncoder)

    def __str__(self):
        return self.plugin_class.get_identifier(self)

    def save(self, *args, **kwargs):
        self.plugin_class.sanitize_model(self)
        self._glossary = None
        super().save(*args, **kwargs)

    @property
    def data(self):
        ''' raw glossary data
        '''
        return self._json

    @data.setter
    def data(self, value:dict):
        self._json = value

    @property
    def glossary(self):
        if not getattr(self, '_glossary', None):
            self._glossary = self.plugin_class.get_glossary(self)
        return self._glossary

    @property
    def label(self):
        return self.glossary.get('label', '')

    def get_short_description(self):
        ''' you may put a label field into the form to give the plugin a label
        for the cms structure view
        '''
        return self.plugin_class.get_identifier(self)

    @cached_property
    def plugin_class(self):
        return self.get_plugin_class()

    @property
    def tag_type(self):
        return self.plugin_class.get_tag_type(self)

    @property
    def css_classes(self):
        css_classes = self.plugin_class.get_css_classes(self)
        return mark_safe(' '.join(c for c in css_classes if c))

    @property
    def inline_styles(self):
        inline_styles = self.plugin_class.get_inline_styles(self)
        return format_html_join(' ', '{0}: {1};', (s for s in inline_styles.items() if s[1]))

    @property
    def html_tag_attributes(self):
        attributes = self.plugin_class.get_html_tag_attributes(self)
        joined = format_html_join(' ', '{0}="{1}"',
            ((attr, val) for attr, val in attributes.items() if val))
        if joined:
            return mark_safe(' ' + joined)
        return ''


class LinkPluginMixin(object):
    """
    A mixin class to inherit a PlusPlugin Model to a proxy model with some
    additional helper methods regarding link handling.

    The LinkPluginMixin model class has to be used to create an extended mdl
    with the LinkPluginBaseMixin together inside a new Custom Plugin Class, e.g.

    class ImagePluginModel(PlusPlugin, LinkPluginMixin):
        class Meta:
            proxy = True

    class ImagePlugin(LinkPluginBase):
        ...
        name = 'Image'
        model = ImagePluginModel
        ...
    """
    plugin_class = None
    glossary = None

    @property
    def link(self):
        return self.plugin_class.get_link(self)

    @property
    def content(self):
        return mark_safe(self.glossary.get('link_content', ''))

    @property
    def download_name(self):
        return self.plugin_class.get_download_name(self)
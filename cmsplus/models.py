import os

from cms.models import CMSPlugin
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.functional import cached_property
from django.utils.html import mark_safe, format_html_join
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from cmsplus.app_settings import cmsplus_settings as cps


class PlusPlugin(CMSPlugin):
    """
    BaseModel for plugins including the important json field.
    """
    _json = JSONField(dump_kwargs={'cls': cps.JSON_ENCODER_CLASS})

    def __str__(self):
        return self.plugin_class.get_identifier(self)

    def save(self, *args, **kwargs):
        self.plugin_class.sanitize_model(self)
        self._glossary = None
        super().save(*args, **kwargs)

    @property
    def data(self):
        """ raw glossary data """
        return self._json

    @data.setter
    def data(self, value: dict):  # noqa E999
        self._json = value

    @property
    def glossary(self):
        if not getattr(self, '_glossary', None):
            self._glossary = self.plugin_class.get_glossary(self)
        return self._glossary

    @property
    def errors(self):
        glossary = self.plugin_class.get_glossary(self)
        form = self.plugin_class.form(data=glossary)
        return form.errors

    @property
    def label(self):
        return self.glossary.get('label', '')

    def get_short_description(self):
        """
        You may put a label field into the form to give the plugin a label
        for the cms structure view.
        """
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
        joined = format_html_join(' ', '{0}="{1}"', ((attr, val) for attr, val in attributes.items() if val))
        if joined:
            return mark_safe(' ' + joined)
        return ''

    @property
    def extra_css(self):
        """
        returns e.g: [
            ('default', 'margin-bottom:2rem;border:2px solid black'),
            ('@media (min-width: 768px)', 'margin-bottom:3rem)'
        ]
        """
        return self.glossary.get('extra_css')
        # css = []
        # for media, css_lines in self.plugin_class.get_extra_css(self).items():
        #     _css = ';'.join(['%s:%s' % (k, v) for k, v in css_lines])
        #     css.append((media, _css))


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
    def download(self):
        return self.plugin_class.is_download(self)

    @property
    def content(self):
        return mark_safe(self.glossary.get('link_content', '') if self.glossary else None)

    @property
    def download_name(self):
        return self.plugin_class.get_download_name(self)


class SCSSStorage(FileSystemStorage):
    def __init__(self, file_permissions_mode=None, directory_permissions_mode=None):
        location = os.path.join('cmsplus', 'static', cps.SITE_STYLES_DIR)
        base_url = os.path.join(settings.STATIC_URL, cps.SITE_STYLES_DIR)
        if not os.path.exists(location):
            os.makedirs(location)
        super().__init__(location, base_url, file_permissions_mode, directory_permissions_mode)


scss_storage = SCSSStorage()


class SiteStyle(models.Model):
    name = models.SlugField(_('Name'), max_length=255, unique=True)
    file = models.FileField(null=True, blank=True, editable=False, storage=scss_storage)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    @property
    def path_for_template(self):
        return os.path.join(cps.SITE_STYLES_DIR, self.file.name)

    def generate_file_name(self):
        return f'{self.name}.scss'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(SiteStyle, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        scss_storage.delete(self.file.name)
        return super().delete(using, keep_parents)

    class Meta:
        verbose_name = _('Site Style')
        verbose_name_plural = _('Site Styles')
        app_label = 'cmsplus'
        ordering = ['order']

    def __str__(self):
        _add = "NO FILE"
        if self.file:
            _add = f'{self.file.name}'
        return f'{self.name}  ({_add})'.strip()

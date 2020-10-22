from cms.plugin_base import CMSPluginBase
from django.utils.safestring import mark_safe
from filer.models.filemodels import File as FilerFileModel

from cmsplus.app_settings import cmsplus_settings as cps
from cmsplus.forms import PlusPluginFormBase
from cmsplus.models import PlusPlugin


class PlusPluginBase(CMSPluginBase):
    form = PlusPluginFormBase
    model = PlusPlugin

    @classmethod
    def get_glossary(cls, instance):
        form = cls.form(instance.data)
        return form.deserialize()

    def save_form(self, request, form, change):
        """
        Set CMSPlugin required attributes
        """
        obj = form.save(commit=False)

        for field, value in self._cms_initial_attributes.items():
            # Set the initial attribute hooks (if any)
            setattr(obj, field, value)

        return obj

    @classmethod
    def sanitize_model(cls, instance):
        """
        This method is called, before the model is saved to the database. It can be overloaded to sanitize the current
        (_json) data dict of the instance.
        """
        if instance.data is None:
            instance.data = {}

    @classmethod
    def get_identifier(cls, instance):
        """
        Hook to return a description for the current model.

        If there is a choice field 'extra_styles' in the plugins form: try to get plugins identifier via the current
        selected extra style name.
        """
        return instance.label

    @classmethod
    def get_tag_type(cls, instance):
        """
        Return the tag_type used to render this plugin.
        """
        return instance.glossary.get('tag_type', getattr(cls, 'tag_type', ''))

    @classmethod
    def get_css_classes(cls, instance):
        """
        Returns a list of CSS classes to be added as class="..." to the current HTML tag.
        """
        if getattr(cls, 'default_css_class', None):
            css_classes = [cls.default_css_class, ]
        else:
            css_classes = []
        return css_classes

    @classmethod
    def get_inline_styles(cls, instance):
        """
        Returns a dictionary of CSS attributes to be added as style="..." to the current HTML tag.  Inline styles can
        be defined in the plugin class via:
        - default_inline_styles = { 'min-height': 'initial', ... }
        - inline_style_map = { 'fixed_height': 'height' }
        """
        inline_styles = getattr(cls, 'default_inline_styles', {})
        style_map = getattr(cls, 'inline_style_map', {})
        if style_map:
            inline_styles.update(
                [(style, instance.glossary.get(key, '')) for key, style in style_map.items()])
        return inline_styles

    @classmethod
    def get_html_tag_attributes(cls, instance):
        """
        Returns a dictionary of attributes, which shall be added to the current HTML tag.
        Tag attributes can be defined in the plugin class via:
        - tag_attr_map = { 'image_title': 'title' } - where image_title defines the
          glossary key which holds the value for the final tag attribute `title`.
        """
        attrs = getattr(cls, 'tag_attr_map', {})
        return dict((attr, instance.glossary.get(key, '')) for key, attr in attrs.items())

    @classmethod
    def get_extra_css(cls, instance):
        """
        Hook to return extra plugin css styles related to devices, e.g.:
        {
            'default' : [
                ('margin-bottom', '2rem'),
                ('border', '2px solid black'),
            ],
            '@media (min-width: 768px)' : [
                ('margin-bottom', '5rem'),
            ],
            ...
        }
        """
        return {}


class StylePluginMixin(object):
    """
    Mixin for PlusPluginBase class to provide a label and extra css styles and classes.

    Extends get_identifier, get_css_classes, get_extra_css
    """
    css_class_fields = ['extra_style', 'extra_classes', ]

    def get_render_template(self, context, instance, placeholder):
        """ try to eval a template based on dirname of render_template and given
        extra_style name, e.g.: 'phoenix/plugins/c-category-tile.html'
        """
        if not getattr(self, 'render_template', None):
            return super().get_render_template(context, instance, placeholder)

        if not instance.glossary.get('extra_style'):
            return self.render_template

        style_template = getattr(
            cps, 'EXTRA_STYLE_TEMPLATES', {}).get(instance.glossary.get('extra_style'))
        if not style_template:
            return self.render_template

        return style_template

    @classmethod
    def get_identifier(cls, instance):
        """
        If there is a choice field 'extra_styles' in the plugins form: try to get plugins identifier via the current
        selected extra style name.
        """
        if instance.label:
            return instance.label
        elif instance.glossary.get('extra_style'):
            try:
                form = getattr(cls, 'form')
                choice_key = getattr(form, 'STYLE_CHOICES')
                style_map = dict(getattr(cps, choice_key))
                return style_map[instance.glossary.get('extra_style')]
            except Exception:
                return instance.glossary.get('extra_style')
        elif instance.glossary.get('extra_classes'):
                return instance.glossary.get('extra_classes')
        return ''

    @classmethod
    def get_css_classes(cls, instance):
        """
        adds all content from css_class_fields to css_classes.
        """
        css_classes = super().get_css_classes(instance)

        if instance.glossary.get('extra_css', None):
            # add a class for instance specific css
            css_classes.append('c-extra-%s' % instance.id)

        for k in getattr(cls, 'css_class_fields', []):
            xc = instance.glossary.get(k)
            if isinstance(xc, str):
                css_classes.append(xc)
            elif isinstance(xc, list):
                css_classes.extend(xc)
        return css_classes

    @classmethod
    def get_extra_css(cls, instance):
        """
        gets the extra (device specific) css styles

        extra_css is stored device specific in glossary like this:
        extra_css : {
            'margin-bottom': '7rem',
            'margin-bottom:md': '13rem',
            'margin-bottom:xl': '30rem',
            'color': 'red',
            'color:md': 'blue',
        }

        returns from example:
            [
                'default', [
                    ('margin-bottom', '7rem'),
                    ('color', 'red'),
                ],
                '@media (min-width: 768px)', [
                    ('margin-bottom', '13rem'),
                    ('color', 'blue'),
                ],
                '@media (min-width: 768px)', [
                    ('margin-bottom', '30rem'),
                ],
            ]
        """

        def _get_media_and_css_key(key):
            """
            from e.g: margin-bottom:md ->  returns '@media (min-width: 768px)', margin-bottom
            """
            try:
                # k e.g. md:margin-bottom
                css_key, dev = key.split(':')
                media = '@media (min-width: %spx)' % cps.DEVICE_MIN_WIDTH_MAP.get(dev, 'xs')
            except ValueError:
                css_key = key
                media = 'default'
            return media, css_key

        css = super().get_extra_css(instance)

        for key, val in instance.glossary.get('extra_css', {}).items():
            media, css_key = _get_media_and_css_key(key)
            if media in css:
                _list = css[media]
                _list.append((css_key, val))
                css[media] = _list
            else:
                css[media] = [(css_key, val), ]
        return css


class LinkPluginBase(PlusPluginBase):
    """
    Base Class to provide a PlusPluginBase with link helper methods.
    """
    allow_children = False
    require_parent = False

    class Media:
        js = ('cmsplus/admin/link_plugin/js/link_plugin.js',)

    @classmethod
    def get_link(cls, instance):
        glossary = instance.glossary
        link_type = glossary.get('link_type', '')
        if link_type == 'exturl':
            return '{ext_url}'.format(**glossary)
        if link_type == 'email':
            return 'mailto:{mail_to}'.format(**glossary)

        # otherwise, resolve by model glossary
        if link_type == 'cmspage':
            relobj = glossary.get('cms_page', None)
            if relobj:
                href = relobj.get_absolute_url()
                if glossary.get('section'):
                    href = '{}#{}'.format(href, glossary.get('section'))
                return href
        elif link_type == 'download':
            relobj = glossary.get('download_file', None)
            if isinstance(relobj, FilerFileModel):
                return relobj.url
        return link_type

    @classmethod
    def get_download_name(cls, instance):
        link_type = instance.glossary.get('link_type', '')
        if link_type == 'download':
            relobj = instance.glossary.get('download_file', None)
            if isinstance(relobj, FilerFileModel):
                return mark_safe(relobj.original_filename)

    @classmethod
    def is_download(cls, instance):
        link_type = instance.glossary.get('link_type', '')
        if link_type == 'download' and not instance.glossary.get('file_as_page'):
            return True
        return False

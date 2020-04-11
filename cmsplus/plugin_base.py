from django.utils.safestring import mark_safe

from cms.plugin_base import CMSPluginBase

from cmsplus.forms import PlusPluginFormBase
from cmsplus.models import PlusPlugin


class PlusPluginBase(CMSPluginBase):
    form = PlusPluginFormBase
    model = PlusPlugin
    template_record_key = "record"

    @classmethod
    def get_record(cls, instance):
        return cls.form.deserialize(instance.glossary)

    def render(self, context, instance, placeholder):
        # record is the deserialized form of the glossary
        context[self.template_record_key] = self.get_record(instance)
        return super().render(context, instance, placeholder)

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Get form and if there is already an instance call the deserialization method to get initial values.
        """
        form = super().get_form(request, obj, change, **kwargs)
        if not obj:
            return form

        record = self.get_record(obj)
        for field_key, field in self.form.declared_fields.items():
            form.declared_fields[field_key].initial = record.get(field_key) or field.initial
        return form

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
    def get_identifier(cls, instance):
        """
        Hook to return a description for the current model.
        """
        return instance.label

    @classmethod
    def get_tag_type(self, instance):
        """
        Return the tag_type used to render this plugin.
        """
        return instance.glossary.get('tag_type', getattr(self, 'tag_type', ''))

    @classmethod
    def get_css_classes(cls, instance):
        """
        Returns a list of CSS classes to be added as class="..." to the current HTML tag.
        """
        css_classes = []
        record = cls.get_record(instance)
        for k in getattr(cls, 'css_class_fields', []):

            xc = record.get(k)
            if isinstance(xc, str):
                css_classes.append(xc)
            elif isinstance(xc, list):
                css_classes.extend(xc)
        return css_classes

    @classmethod
    def get_html_tag_attributes(cls, instance):
        """
        Returns a dictionary of attributes, which shall be added to the current HTML tag.
        This method normally is called by the models's property method ``html_tag_ attributes``,
        which enriches the HTML tag with those attributes converted to a list as
        ``attr1="val1" attr2="val2" ...``.
        """
        attrs = getattr(cls, 'html_tag_attributes', {})
        return dict((attr, instance.glossary.get(key, '')) for key, attr in attrs.items())


# Base Class to provide plugin help, a label and extra style css classes
# ----------------------------------------------------------------------
# TODO: active Help later - see plugin_change_form
#class CssLabelPluginMixin(PluginHelpMixin):
class StylePluginMixin(object):
    css_class_fields = ['extra_style', 'extra_classes',]

    def get_render_template(self, context, instance, placeholder):
        ''' try to eval a template based on dirname of render_template and given
        extra_style name, e.g.: 'phoenix/plugins/c-category-tile.html'
        '''
        if not getattr(self, 'render_template', None):
            return super().get_render_template(context, instance, placeholder)

        if not instance.glossary.get('extra_style'):
            return self.render_template

        style_template = getattr(settings, 'EXTRA_STYLE_TEMPLATES',
                {}).get(instance.glossary.get('extra_style'))
        if not style_template:
            return self.render_template

        return style_template

    @classmethod
    def get_identifier(cls, obj):
        label = obj.glossary.get('label', None)
        if label: return label

        if obj.glossary.get('extra_style'):
            try:
                form = getattr(cls, 'form')
                choice_key = getattr(form, 'STYLE_CHOICES')
                style_map = dict(getattr(settings, choice_key))
                return style_map[obj.glossary.get('extra_style')]
            except:
                return obj.glossary.get('extra_style')
        return super().get_identifier(obj)


# Base Class to provide a PlusPluginBase with link helper methods
# ---------------------------------------------------------------
#
class LinkPluginBase(PlusPluginBase):
    allow_children = False
    parent_classes = []
    require_parent = False
    ring_plugin = 'LinkPluginBase'
    html_tag_attributes = {'title': 'title', 'target': 'target'}

    #class Media:
        #js = ['admin/js/jquery.init.js', 'cascade/js/admin/linkplugin.js']

    @classmethod
    def get_link(cls, instance):
        record = cls.get_record(instance)
        link_type = record.get('link_type', '')
        if link_type == 'exturl':
            return '{ext_url}'.format(**instance.glossary)
        if link_type == 'email':
            return 'mailto:{mail_to}'.format(**instance.glossary)

        # otherwise resolve by model record
        if link_type == 'cmspage':
            relobj = record.get('cms_page', None)
            if relobj:
                href = relobj.get_absolute_url()
                if record.get('section'):
                    href = '{}#{}'.format(href, record.get('section'))
                return href
        elif link_type == 'download':
            relobj = record.get('download_file', None)
            if isinstance(relobj, FilerFileModel):
                return relobj.url
        return link_type

    @classmethod
    def get_download_name(cls, instance):
        record = cls.get_record(instance)
        link_type = record.get('link_type', '')
        if link_type == 'download':
            relobj = record.get('download_file', None)
            if isinstance(relobj, FilerFileModel):
                return mark_safe(relobj.original_filename)

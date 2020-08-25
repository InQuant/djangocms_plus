from importlib import import_module

from cms.api import create_page, add_plugin
from cms.models import Page
from cms.plugin_pool import plugin_pool
from django.forms.fields import CharField, ChoiceField, MultipleChoiceField, URLField, EmailField, IntegerField, \
    BooleanField, FloatField
from django.test import TestCase
from faker import Faker

from cmsplus.app_settings import cmsplus_settings
from cmsplus.plugin_base import PlusPluginBase
from cmsplus.tests.forms import TestForm


@plugin_pool.register_plugin
class ExamplePlugin(PlusPluginBase):
    form = TestForm
    render_template = "test_plugin.html"
    name = 'Test'
    module = 'test'


class TestAllIncludedPlugins(TestCase):
    def setUp(self) -> None:
        self.settings = cmsplus_settings
        self.fake = Faker()
        self.page = create_page(
            title="Test page",
            template="home.html",
            language="en-us",
        )   # type: Page

    @staticmethod
    def get_class(plugin_str):
        mod_name, cls_name = plugin_str.rsplit('.', 1)
        mod = import_module(mod_name)
        cls = getattr(mod, cls_name)
        return cls

    def test_plugins(self):
        """
        Test adding Plugins to Page
        :return:
        """
        placeholder = self.page.placeholders.get(slot='content')
        for plugin_str in self.settings.PLUGINS:
            data = {}
            plugin_cls = self.get_class(plugin_str)     # type: PlusPluginBase
            for field in plugin_cls.form.base_fields:
                field_cls = plugin_cls.form.declared_fields[field]

                if issubclass(field_cls.__class__, CharField):
                    data[field] = self.fake.text(255)

                elif issubclass(field_cls.__class__, ChoiceField) or \
                        issubclass(field_cls.__class__, MultipleChoiceField):
                    choices = list(field_cls.choices)
                    if len(choices) > 0:
                        data[field] = 10

                elif issubclass(field_cls.__class__, URLField):
                    data[field] = self.fake.url()

                elif issubclass(field_cls.__class__, EmailField):
                    data[field] = self.fake.email()

                elif issubclass(field_cls.__class__, IntegerField):
                    data[field] = self.fake.random_int()

                elif issubclass(field_cls.__class__, BooleanField):
                    data[field] = self.fake.boolean()

                elif issubclass(field_cls.__class__, FloatField):
                    data[field] = self.fake.random_float()

            plugin = add_plugin(
                placeholder=placeholder,
                plugin_type=plugin_cls,
                language='en-us',
                data=data
            )
            self.assertIsNotNone(plugin.id, "Could not create and add the plugin '%s'" % (plugin_str,))

        self.page.publish('en-us')
        self.assertTrue(self.page.is_published('en-us'), "Could not publish Page with plugins")
        self.page.unpublish('en-us')
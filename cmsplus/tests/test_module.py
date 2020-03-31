from pprint import pprint

from cms.api import add_plugin, create_page
from cms.models import Placeholder
from cms.test_utils.testcases import CMSTestCase
from django.contrib import admin
from django.template import Context
from django.test import TestCase, RequestFactory

from .cms_plugins import ExamplePlugin


class ModuleTest(CMSTestCase):
    home_page = None

    def test_save(self):
        home_page = create_page(title='HOME', template='test_plugin.html', language='en')
        placeholder = home_page.placeholders.get(slot='col_left')
        context = self.get_context('/', page=home_page)
        plugin = ExamplePlugin()
        new_context = plugin.render(context, None, placeholder)
        pprint(new_context)

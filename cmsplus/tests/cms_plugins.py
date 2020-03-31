from cms.plugin_pool import plugin_pool

from cmsplus.plugin_base import PlusPluginBase
from cmsplus.tests.forms import TestForm


@plugin_pool.register_plugin
class ExamplePlugin(PlusPluginBase):
    form = TestForm
    render_template = "test_plugin.html"

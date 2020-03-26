from cms.plugin_pool import plugin_pool
from django import forms

from djangocms_plus.fields import PlusModelMultipleChoiceField
from djangocms_plus.forms import PlusPluginBaseForm
from djangocms_plus.models import Test
from djangocms_plus.plugin_base import PlusCMSPluginBase


class TestForm(PlusPluginBaseForm):
    test = forms.EmailField()
    test2 = PlusModelMultipleChoiceField(queryset=Test.objects.all())


@plugin_pool.register_plugin
class ExamplePluginPlus(PlusCMSPluginBase):
    form = TestForm
    render_template = "test.html"

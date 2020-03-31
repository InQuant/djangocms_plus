from cms.plugin_pool import plugin_pool
from django import forms

from cmsplus.forms import PlusPluginBaseForm
from cmsplus.plugin_base import PlusPluginBase


class TestForm(PlusPluginBaseForm):
    test = forms.EmailField()

    # Examples with Models
    # test2 = PlusModelMultipleChoiceField(queryset=Test.objects.all())
    # test2 = PlusModelChoiceField(queryset=Test.objects.all())


@plugin_pool.register_plugin
class ExamplePluginPlus(PlusPluginBase):
    form = TestForm
    render_template = "test.html"

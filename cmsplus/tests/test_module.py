from cms.api import add_plugin
from cms.models import Placeholder
from cms.plugin_rendering import ContentRenderer
from cms.test_utils.testcases import CMSTestCase
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.test import RequestFactory

from cmsplus.cms_plugins.generic.icon import IconPlugin, IconFieldWidget
from cmsplus.tests.cms_plugins import ExamplePlugin
from cmsplus.tests.models import Test


class ModuleTest(CMSTestCase):
    def setUp(self) -> None:
        self.t1 = Test.objects.create(
            message='Test Message 1',
        )
        self.t2 = Test.objects.create(
            message='Test Message 2',
        )
        User.objects.create(
            username="admin",
            password="test",
            first_name="test",
            last_name="test",
        )

    def test_serialize_and_deserialize(self):
        choice_1 = ExamplePlugin.form.base_fields['test_model_choice'].choices.queryset[0]
        data = {
            'test_email': 'example@example.com',
            'test_model_choice': choice_1.id,
            'test_model_multiple_choice': Test.objects.all(),
        }
        form = ExamplePlugin.form(data)
        self.assertTrue(form.is_valid(), "Form validation not working as expected")

        model_instance = add_plugin(
            Placeholder.objects.create(slot='test'),
            ExamplePlugin,
            'en',
            data=form.serialize_data()
        )

        plugin_instance = model_instance.get_plugin_class_instance()
        context = plugin_instance.render({}, model_instance, None)

        self.assertEqual(data['test_email'], context['instance'].glossary['test_email'],
                         "EmailField output differs from input.")

        self.assertEqual(context['instance'].glossary['test_model_choice'], choice_1,
                         "ModelChoice input and output is not the same. Check 'PlusModelChoiceField'.")

        r = context['instance'].glossary['test_model_multiple_choice']
        self.assertListEqual([o.id for o in r], [o.id for o in data['test_model_multiple_choice']],
                             "ModelMultipleChoice input and output is not the same. "
                             "Check 'PlusModelMultipleChoiceField'")

        deserialized_data = dict(ExamplePlugin.form.deserialize(form.serialize_data()))

        self.assertEqual(data['test_email'], deserialized_data['test_email'], "Test Email is not equal")
        self.assertEqual(data['test_model_choice'], deserialized_data['test_model_choice'].id, "Model Choice not equal")
        self.assertEqual(len(data['test_model_multiple_choice']),
                         len(deserialized_data['test_model_multiple_choice']), "Model Choice Multiple not equal")

    def test_plugin_icon(self):
        icon_widget = IconFieldWidget()
        self.assertTrue(isinstance(icon_widget.get_fontawesome_icons, list), "Could not get Fontawesome icon list")
        self.assertGreaterEqual(len(icon_widget.get_fontawesome_icons), 0, "Could not get any Fontawesome icons")

        data = {'icon': 'fab fa-bible'}
        placeholder = Placeholder.objects.create(slot='content')
        model_instance = add_plugin(
            placeholder,
            IconPlugin,
            'en',
            data=data
        )
        plugin_instance = model_instance.get_plugin_class_instance()
        context = plugin_instance.render({}, model_instance, None)

        self.assertDictEqual(data, context['instance']._json, "_json field data is not as expected")

        renderer = ContentRenderer(request=RequestFactory())
        html = renderer.render_plugin(model_instance, {})

        test_context = {'instance': {'glossary': data}}
        test_html = render_to_string(template_name=IconPlugin.render_template,
                                     context=test_context, request=RequestFactory())

        self.assertHTMLEqual(test_html, html, "Rendered HTML differs from what it should be")

from django.test import TestCase

from cmsplus.admin import SiteStyleForm
from cmsplus.models import scss_storage


class SiteStyle(TestCase):

    def test_create_style_with_form(self):
        form_data = {
            'name': 'test',
            'content': 'Lorem Ipsum'
        }
        form = SiteStyleForm(data=form_data)
        self.assertTrue(form.is_valid(), 'Form was invalid?!')

        r = form.save(commit=True)
        self.assertEqual(form_data.get('name'), r.name)
        with r.file.open('r') as f:
            content = f.read()

        self.assertEqual(form_data.get('content'), content)

        self.assertTrue(scss_storage.exists(r.file.name))
        scss_storage.delete(r.file.name)
        self.assertFalse(scss_storage.exists(r.file.name))
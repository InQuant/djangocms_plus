from django import forms

from cmsplus.fields import PlusModelMultipleChoiceField, PlusModelChoiceField
from cmsplus.forms import PlusPluginFormBase
from cmsplus.tests.models import Test


class TestForm(PlusPluginFormBase):
    test_email = forms.EmailField()
    test_model_choice = PlusModelChoiceField(queryset=Test.objects.all())
    test_model_multiple_choice = PlusModelMultipleChoiceField(queryset=Test.objects.all())

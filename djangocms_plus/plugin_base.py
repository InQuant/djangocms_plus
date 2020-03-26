from cms.plugin_base import CMSPluginBase

from djangocms_plus.forms import PlusPluginBaseForm
from djangocms_plus.models import PlusPlugin


class PlusCMSPluginBase(CMSPluginBase):
    model = PlusPlugin
    form = PlusPluginBaseForm
    template_data_label = "data"

    def __init__(self, *args, **kwargs):
        assert issubclass(self.form, PlusPluginBaseForm), "%s should have %s as subclass" % (
            self.form.__name__, PlusPluginBaseForm.__name__
        )
        super().__init__(*args, **kwargs)

    def render(self, context, instance, placeholder):
        context[self.template_data_label or "data"] = self.form.deserialize(instance.json)
        return super().render(context, instance, placeholder)

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Get form and if there is already an instance call the deserialization method to get initial values.
        """
        form = super().get_form(request, obj, change, **kwargs)
        if not obj:
            return form

        data = self.form.deserialize(obj.json)
        for field_key, field in self.form.declared_fields.items():
            form.declared_fields[field_key].initial = data.get(field_key) or field.initial
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
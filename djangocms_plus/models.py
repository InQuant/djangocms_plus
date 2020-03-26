import jsonfield
from cms.models import CMSPlugin
from django.db import models

from djangocms_plus.utils import JSONEncoder


class PlusPlugin(CMSPlugin):
    """
    BaseModel for plugins including the important json field.
    """

    _json = jsonfield.JSONField(encoder_class=JSONEncoder)

    @property
    def json(self):
        return self._json

    @json.setter
    def json(self, value):
        self._json = value


class Test(models.Model):
    test_feld = models.CharField(default="test", max_length=200)

import jsonfield
from cms.models import CMSPlugin
from django.db import models

from djangocms_plus.utils import JSONEncoder


class PlusPlugin(CMSPlugin):
    _json = jsonfield.JSONField(encoder_class=JSONEncoder)

    def get_json(self):
        return self._json

    def set_json(self, value):
        self._json = value


class Test(models.Model):
    test_feld = models.CharField(default="test", max_length=200)

from cms.models import CMSPlugin
from jsonfield import JSONField

from cmsplus.utils import JSONEncoder


class PlusPlugin(CMSPlugin):
    """
    BaseModel for plugins including the important json field.
    """

    _json = JSONField(encoder_class=JSONEncoder)

    @property
    def json(self):
        return self._json

    @json.setter
    def json(self, value):
        self._json = value

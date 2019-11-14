from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import MEGABYTE


class StringType(PropertyType):
    name = 'string'
    label = _('Label')
    plural = _('Labels')
    matchable = False


class TextType(PropertyType):
    name = 'text'
    label = _('Text')
    matchable = False
    max_size = 30 * MEGABYTE

    def node_id(self, value):
        return None


class HTMLType(PropertyType):
    name = 'html'
    label = _('HTML')
    matchable = False
    max_size = 30 * MEGABYTE

    def node_id(self, value):
        return None

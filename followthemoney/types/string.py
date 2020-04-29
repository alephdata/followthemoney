from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import MEGABYTE


class StringType(PropertyType):
    name: str = 'string'
    label: str = _('Label')
    plural: str = _('Labels')
    matchable: bool = False


class TextType(PropertyType):
    name: str = 'text'
    label: str = _('Text')
    matchable: bool = False
    max_size: int = 30 * MEGABYTE

    def node_id(self, value):
        return None


class HTMLType(PropertyType):
    name: str = 'html'
    label: str = _('HTML')
    matchable: bool = False
    max_size: int = 30 * MEGABYTE

    def node_id(self, value):
        return None

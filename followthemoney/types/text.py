from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import MEGABYTE


class TextType(PropertyType):
    name = 'text'
    label = _('Text')
    matchable = False
    max_size = 100 * MEGABYTE

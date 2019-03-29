from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class TextType(PropertyType):
    name = 'text'
    label = _('Text')
    matchable = False

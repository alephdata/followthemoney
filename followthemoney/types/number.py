from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class NumberType(PropertyType):
    name = 'number'
    label = _('Number')
    plural = _('Numbers')
    matchable = False

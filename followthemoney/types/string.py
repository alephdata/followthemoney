from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class StringType(PropertyType):
    name = 'string'
    label = _('Label')
    plural = _('Labels')
    matchable = False

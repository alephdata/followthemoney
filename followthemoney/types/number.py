import re

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class NumberType(PropertyType):
    name = 'number'
    label = _('Number')
    plural = _('Numbers')
    matchable = False

    def _cast_num(self, value):
        value = re.sub(r'[^0-9\-\.]', '', value)
        return float(value)

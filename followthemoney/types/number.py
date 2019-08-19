import re

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class NumberType(PropertyType):
    CAST_RE = re.compile(r'[^0-9\-\.]')
    name = 'number'
    label = _('Number')
    plural = _('Numbers')
    matchable = False

    def to_number(self, value):
        try:
            value = self.CAST_RE.sub('', value)
            return float(value)
        except Exception:
            return

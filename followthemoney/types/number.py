import re
from typing import Any, Optional

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class NumberType(PropertyType):
    CAST_RE = re.compile(r'[^0-9\-\.]')
    name: str = 'number'
    label: str = _('Number')
    plural: str = _('Numbers')
    matchable: bool = False

    def to_number(self, value: Any) -> Optional[float]:
        try:
            value = self.CAST_RE.sub('', value)
            return float(value)
        except Exception:
            return None

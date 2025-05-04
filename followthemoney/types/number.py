import re
from typing import Optional, Tuple

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class NumberType(PropertyType):
    """A numeric value, like the size of a piece of land, or the value of a
    contract. Since all property values in FtM are strings, this is also a
    string and there is no specified format (e.g. `1,000.00` vs. `1.000,00`).

    In the future we might want to enable annotations for format, units, or
    even to introduce a separate property type for monetary values."""

    CAST_RE = re.compile(r"[^0-9\-\.]")
    name = "number"
    label = _("Number")
    plural = _("Numbers")
    matchable = False

    def node_id(self, value: str) -> None:
        return None

    def parse(self, value: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse a number value into a tuple of (number, unit). The number format
        must be NNN,NNN.DD (commas as display separators, dot for decimal separator).
        The unit cannot start with a number, and may be separated from the number by
        a space."""

    def to_number(self, value: str) -> Optional[float]:
        try:
            value = self.CAST_RE.sub("", value)
            return float(value)
        except Exception:
            return None

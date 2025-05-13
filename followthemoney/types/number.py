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

    DECIMAL = "."
    SEPARATOR = ","
    PRECISION = 2

    _NUM_UNIT_RE = (
        f"(\\s?\\-?\\s?\\d+(?:{re.escape(DECIMAL)}\\d+)?)\\s*([^\\s\\d][^\\s]*)?"
    )
    NUM_UNIT_RE = re.compile(_NUM_UNIT_RE, re.UNICODE)
    _FLOAT_FMT = "{:" + SEPARATOR + "." + str(PRECISION) + "f}"
    _INT_FMT = "{:" + SEPARATOR + "d}"

    name = "number"
    label = _("Number")
    plural = _("Numbers")
    matchable = False

    def node_id(self, value: str) -> None:
        return None

    def parse(
        self, value: str, decimal: str = DECIMAL, separator: str = SEPARATOR
    ) -> Tuple[Optional[str], Optional[str]]:
        """Parse a number into a numeric value and a unit. The numeric value is
        aligned with the decimal and separator settings. The unit is stripped of
        whitespace and returned as a string. If no unit is found, None is
        returned. If no number is found, None is returned for both values."""
        value = value.replace(separator, "")
        if decimal != self.DECIMAL:
            value = value.replace(decimal, self.DECIMAL)
        match = self.NUM_UNIT_RE.match(value)
        if not match:
            return None, None
        number, unit = match.groups()
        if unit is not None:
            unit = unit.strip()
            if len(unit) == 0:
                unit = None
        # TODO: We could have a lookup table for common units, e.g. kg, m, etc. to
        # convert them to a standard form.
        number = number.replace(" ", "")
        if number == "":
            number = None
        return number, unit

    def to_number(self, value: str) -> Optional[float]:
        try:
            number, _ = self.parse(value)
            if number is None:
                return None
            return float(number)
        except Exception:
            return None

    def caption(self, value: str, format: Optional[str] = None) -> str:
        """Return a caption for the number. This is used for display purposes."""
        number, unit = self.parse(value)
        if number is None:
            return value
        try:
            fnumber = float(number)
        except ValueError:
            return value
        if format is not None:
            number = format.format(fnumber)
        elif fnumber.is_integer():
            number = self._INT_FMT.format(int(fnumber))
        else:
            number = self._FLOAT_FMT.format(fnumber)
        if unit is not None:
            return f"{number} {unit}"
        return number

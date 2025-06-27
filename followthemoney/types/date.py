import os
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from prefixdate import parse, parse_format, Precision

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import dampen

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class DateType(PropertyType):
    """A date or time stamp. This is based on ISO 8601, but meant to allow for different
    degrees of precision by specifying a prefix. This means that `2021`, `2021-02`,
    `2021-02-16`, `2021-02-16T21`, `2021-02-16T21:48` and `2021-02-16T21:48:52`
    are all valid values, with an implied precision.

    The timezone is always expected to be UTC and cannot be specified otherwise. There is
    no support for calendar weeks (`2021-W7`) and date ranges (`2021-2024`)."""

    name = "date"
    group = "dates"
    label = _("Date")
    plural = _("Dates")
    matchable = True
    max_length = 32

    def validate(
        self, value: str, fuzzy: bool = False, format: Optional[str] = None
    ) -> bool:
        """Check if a thing is a valid date."""
        if format is not None:
            prefix = parse_format(value, format)
        else:
            prefix = parse(value)
        return prefix.precision != Precision.EMPTY

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """The classic: date parsing, every which way."""
        if format is not None:
            return parse_format(text, format).text
        return parse(text).text

    def _specificity(self, value: str) -> float:
        return dampen(5, 13, value)

    def compare(self, left: str, right: str) -> float:
        prefix = os.path.commonprefix([left, right])
        return dampen(4, 10, prefix)

    def node_id(self, value: str) -> str:
        return f"date:{value}"

    def to_datetime(self, value: str) -> Optional[datetime]:
        return parse(value).dt

    def to_number(self, value: str) -> Optional[float]:
        date = self.to_datetime(value)
        if date is None:
            return None
        # We make a best effort all over the app to ensure all times are in UTC.
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        return date.timestamp()

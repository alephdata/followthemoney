import re
import os
import pytz
import logging
from rdflib import Literal  # type: ignore
from rdflib.namespace import XSD  # type: ignore
from datetime import datetime, date
from typing import Any, Union, Optional, Dict, List

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import dampen, sanitize_text

log = logging.getLogger(__name__)


class DateType(PropertyType):
    # JS: '^([12]\\d{3}(-[01]?[1-9](-[0123]?[1-9])?)?)?$'
    DATE_RE = re.compile(r'^([12]\d{3}(-[01]?[0-9](-[0123]?[0-9]([T ]([012]?\d(:\d{1,2}(:\d{1,2}(\.\d{6})?(Z|[-+]\d{2}(:?\d{2})?)?)?)?)?)?)?)?)?$')  # noqa
    DATE_FULL = re.compile(r'\d{4}-\d{2}-\d{2}.*')
    CUT_ZEROES = re.compile(r'((\-00.*)|(.00:00:00))$')
    MONTH_FORMATS = re.compile(r'(%b|%B|%m|%c|%x)')
    DAY_FORMATS = re.compile(r'(%d|%w|%c|%x)')
    MAX_LENGTH = 19
    DATE_PATTERNS_BY_LENGTH: Dict[int, List[str]] = {
        19: ["%Y-%m-%dT%H:%M:%S"],
        18: ["%Y-%m-%dT%H:%M:%S"],
        17: ["%Y-%m-%dT%H:%M:%S"],
        16: ["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        15: ["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        14: ["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        13: ["%Y-%m-%dT%H", "%Y-%m-%dT%H:%M"],
        12: ["%Y-%m-%dT%H", "%Y-%m-%dT%H:%M"],
        11: ["%Y-%m-%dT%H"],
        10: ["%Y-%m-%d", "%Y-%m-%dT%H"],
        9: ["%Y-%m-%d"],
        8: ["%Y-%m-%d"],
        7: ["%Y-%m"],
        6: ["%Y-%m"],
        5: [],
        4: ["%Y"],
    }

    name: str = 'date'
    group: str = 'dates'
    label: str = _('Date')
    plural: str = _('Dates')
    matchable: bool = True

    def validate(self, obj: Any, **kwargs) -> bool:  # type: ignore[override] # noqa
        """Check if a thing is a valid date."""
        obj = sanitize_text(obj)
        if obj is None:
            return False
        return self.DATE_RE.match(obj) is not None

    def _clean_datetime(self, obj: Union[datetime, date]) -> str:
        """Python objects want to be text."""
        if isinstance(obj, datetime):
            # if it's not naive, put it on zulu time first:
            if obj.tzinfo is not None:
                obj = obj.astimezone(pytz.utc)
            return obj.isoformat()[:self.MAX_LENGTH]
        else:
            return obj.isoformat()

    def _clean_text(self, text: str) -> Optional[str]:
        # limit to the date part of a presumed date string
        # FIXME: this may get us rid of TZ info?
        text = text[:self.MAX_LENGTH]
        if not self.validate(text):
            return None
        text = text.replace(' ', 'T')
        # fix up dates like 2017-1-5 into 2017-01-05
        if not self.DATE_FULL.match(text):
            parts = text.split('T', 1)
            date = [p.zfill(2) for p in parts[0].split('-')]
            parts[0] = '-'.join(date)
            text = 'T'.join(parts)
            text = text[:self.MAX_LENGTH]
        # strip -00-00 from dates because it makes ES barf.
        text = self.CUT_ZEROES.sub('', text)
        return text

    def clean(self, text: Any, format: str=None, **kwargs) -> Optional[str]:
        """The classic: date parsing, every which way."""
        # handle date/datetime before converting to text.
        if isinstance(text, (date, datetime)):
            return self._clean_datetime(text)

        text = sanitize_text(text)
        if text is None:
            return None

        if format is not None:
            # parse with a specified format
            try:
                obj = datetime.strptime(text, format)
                text = obj.date().isoformat()
                if self.MONTH_FORMATS.search(format) is None:
                    text = text[:4]
                elif self.DAY_FORMATS.search(format) is None:
                    text = text[:7]
                return text
            except Exception:
                return None

        return self._clean_text(text)

    def _specificity(self, value: str) -> float:
        return dampen(5, 13, value)

    def compare(self, left: str, right: str) -> float:
        prefix = os.path.commonprefix([left, right])
        return dampen(4, 10, prefix)

    def rdf(self, value) -> Literal:
        return Literal(value, datatype=XSD.dateTime)

    def node_id(self, value: str) -> str:
        return 'date:%s' % value

    def to_datetime(self, value: str) -> Optional[datetime]:
        formats = self.DATE_PATTERNS_BY_LENGTH.get(len(value), [])
        for fmt in formats:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.replace(tzinfo=pytz.UTC)
            except Exception:
                continue
        log.debug('Date cannot be parsed %r: %s', formats, value)
        return None

    def to_number(self, value):
        date = self.to_datetime(value)
        if date is not None:
            return date.timestamp()

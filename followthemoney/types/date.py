import re
import os
import pytz
from rdflib import Literal
from rdflib.namespace import XSD
from datetime import datetime, date

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import dampen, sanitize_text


class DateType(PropertyType):
    # JS: '^([12]\\d{3}(-[01]?[1-9](-[0123]?[1-9])?)?)?$'
    DATE_RE = re.compile('^([12]\d{3}(-[01]?[0-9](-[0123]?[0-9]([T ]([012]?\d(:\d{1,2}(:\d{1,2}(\.\d{6})?(Z|[-+]\d{2}(:?\d{2})?)?)?)?)?)?)?)?)?$')  # noqa
    DATE_FULL = re.compile(r'\d{4}-\d{2}-\d{2}.*')
    CUT_ZEROES = re.compile(r'((\-00.*)|(.00:00:00))$')
    MONTH_FORMATS = re.compile(r'(%b|%B|%m|%c|%x)')
    DAY_FORMATS = re.compile(r'(%d|%w|%c|%x)')
    MAX_LENGTH = 19

    name = 'date'
    group = 'dates'
    label = _('Date')
    plural = _('Dates')
    matchable = True

    def validate(self, obj, **kwargs):
        """Check if a thing is a valid date."""
        obj = sanitize_text(obj)
        if obj is None:
            return False
        return self.DATE_RE.match(obj) is not None

    def _clean_datetime(self, obj):
        """Python objects want to be text."""
        if isinstance(obj, datetime):
            # if it's not naive, put it on zulu time first:
            if obj.tzinfo is not None:
                obj = obj.astimezone(pytz.utc)
            return obj.isoformat()[:self.MAX_LENGTH]
        if isinstance(obj, date):
            return obj.isoformat()

    def _clean_text(self, text):
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

    def clean(self, text, format=None, **kwargs):
        """The classic: date parsing, every which way."""
        # handle date/datetime before converting to text.
        date = self._clean_datetime(text)
        if date is not None:
            return date

        text = sanitize_text(text)
        if text is None:
            return

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

    def _specificity(self, value):
        return dampen(5, 13, value)

    def compare(self, left, right):
        prefix = os.path.commonprefix([left, right])
        return dampen(4, 10, prefix)

    def rdf(self, value):
        return Literal(value, datatype=XSD.dateTime)

    def _cast_num(self, value):
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H",
            "%Y-%m-%d",
            "%Y-%m",
            "%Y",
        ]
        date = None
        for fmt in formats:
            try:
                date = datetime.strptime(value, fmt)
            except Exception:
                continue
        if date:
            return pytz.utc.localize(date).timestamp()
        else:
            return 0

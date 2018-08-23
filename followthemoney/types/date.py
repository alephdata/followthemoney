import re
import pytz
import parsedatetime
from normality import stringify
from datetime import datetime, date
from dateutil import parser as dateparser

from followthemoney.types.common import PropertyType


class DateType(PropertyType):
    # JS: '^([12]\\d{3}(-[01]?[1-9](-[0123]?[1-9])?)?)?$'
    DATE_RE = re.compile('^([12]\d{3}(-[01]?[0-9](-[0123]?[0-9]([T ]([012]?\d(:\d{1,2}(:\d{1,2}(\.\d{6})?(Z|[-+]\d{2}(:?\d{2})?)?)?)?)?)?)?)?)?$')  # noqa
    DATE_FULL = re.compile('\d{4}-\d{2}-\d{2}.*')
    CUT_ZEROES = re.compile(r'((\-00.*)|(.00:00:00))$')
    MAX_LENGTH = 19

    def validate(self, obj, **kwargs):
        """Check if a thing is a valid date."""
        obj = stringify(obj)
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

    def clean(self, text, guess=True, format=None, **kwargs):
        """The classic: date parsing, every which way."""
        # handle date/datetime before converting to text.
        date = self._clean_datetime(text)
        if date is not None:
            return date

        text = stringify(text)
        if text is None:
            return

        if format is not None:
            # parse with a specified format
            try:
                obj = datetime.strptime(text, format)
                return obj.date().isoformat()
            except Exception:
                return None

        if guess and not self.validate(text):
            # use dateparser to guess the format
            obj = self.fuzzy_date_parser(text)
            if obj is not None:
                return obj.date().isoformat()

        return self._clean_text(text)

    def fuzzy_date_parser(self, text):
        """Thin wrapper around ``parsedatetime`` and ``dateutil`` modules.
        Since there's no upstream suppport for multiple locales, this wrapper
        exists.
        :param str text: Text to parse.
        :returns: A parsed date/time object. Raises exception on failure.
        :rtype: datetime
        """
        try:
            parsed = dateparser.parse(text, dayfirst=True)
            return parsed
        except (ValueError, TypeError):
            locales = parsedatetime._locales[:]
            # Loop through all the locales and try to parse successfully our
            # string
            for locale in locales:
                const = parsedatetime.Constants(locale)
                const.re_option += re.UNICODE
                parser = parsedatetime.Calendar(const)
                parsed, ok = parser.parse(text)
                if ok:
                    return datetime(*parsed[:6])

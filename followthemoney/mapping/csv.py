import io
import os
import logging
import requests
from csv import DictReader
from banal import ensure_list
from normality import stringify

from followthemoney.mapping.source import Source
from followthemoney.exc import InvalidMapping

log = logging.getLogger(__name__)


class CSVSource(Source):
    """Special case for entity loading directly from a CSV URL"""

    def __init__(self, query, data):
        super(CSVSource, self).__init__(query, data)
        urls = ensure_list(data.get('csv_url'))
        urls.extend(ensure_list(data.get('csv_urls')))
        self.urls = set()
        for url in urls:
            self.urls.add(os.path.expandvars(url))

        if not len(self.urls):
            raise InvalidMapping("No CSV URLs are specified.")

    def read_csv(self, url):
        parsed_url = requests.utils.urlparse(url)
        log.info("Loading: %s", url)
        if parsed_url.scheme in ['http', 'https']:
            res = requests.get(url, stream=True)
            if not res.ok:
                raise InvalidMapping("Failed to open CSV: %s" % url)
            # if res.encoding is None:
            res.encoding = 'utf-8'
            # log.info("Detected encoding: %s", res.encoding)
            lines = res.iter_lines(decode_unicode=True)
            for row in DictReader(lines, skipinitialspace=True):
                yield row
        else:
            with io.open(parsed_url.path, 'r') as fh:
                for row in DictReader(fh, skipinitialspace=True):
                    yield row

    def check_filters(self, data):
        for (k, v) in self.filters:
            if v != data.get(k):
                return False
        for (k, v) in self.filters_not:
            if v == data.get(k):
                return False
        return True

    @property
    def records(self):
        """Iterate through the table applying filters on-the-go."""
        for url in self.urls:
            for row in self.read_csv(url):
                data = {}
                for ref in self.query.refs:
                    data[ref] = stringify(row.get(ref))
                if self.check_filters(data):
                    yield data

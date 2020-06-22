import io
import os
import logging
import requests
from banal import keys_values
from normality import stringify

from followthemoney.mapping.source import StreamSource
from followthemoney.exc import InvalidMapping

log = logging.getLogger(__name__)


class CSVSource(StreamSource):
    """Special case for entity loading directly from a CSV URL"""

    def __init__(self, query, data):
        super(CSVSource, self).__init__(query, data)
        self.urls = set()
        for url in keys_values(data, 'csv_url', 'csv_urls'):
            self.urls.add(os.path.expandvars(url))

        if not len(self.urls):
            raise InvalidMapping("No CSV URLs are specified.")

    def read_csv_url(self, url):
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
            yield from self.read_csv(lines)
        else:
            with io.open(parsed_url.path, 'r') as fh:
                yield from self.read_csv(fh)

    @property
    def records(self):
        """Iterate through the table applying filters on-the-go."""
        for url in self.urls:
            for row in self.read_csv_url(url):
                data = {}
                for ref in self.query.refs:
                    data[ref] = stringify(row.get(ref))
                if self.check_filters(row):
                    yield data

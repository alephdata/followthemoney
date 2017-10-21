import os
import requests
from banal import ensure_list
from normality import stringify
from unicodecsv import DictReader

from followthemoney.mapping.source import Source
from followthemoney.exc import InvalidMapping


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

    def read_remote_csv(self, url):
        res = requests.get(url, stream=True)
        if not res.ok:
            raise InvalidMapping("Failed to open CSV: %s" % url)
        if res.encoding is None:
            res.encoding = 'utf-8'
        lines = res.iter_lines(decode_unicode=False)
        for row in DictReader(lines, skipinitialspace=True):
            yield row

    def read_local_csv(self, path):
        with open(path, "r") as f:
            for row in DictReader(f, skipinitialspace=True):
                yield row

    def read_csv(self, csv_url):
        parsed_url = requests.utils.urlparse(csv_url)
        if parsed_url.scheme == 'file':
            return self.read_local_csv(parsed_url.path)
        else:
            return self.read_remote_csv(csv_url)

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
        for csv_url in self.csv_urls:
            for row in self.read_csv(csv_url):
                data = {}
                for ref in self.query.refs:
                    data[ref] = stringify(row.get(ref))
                if self.check_filters(data):
                    yield data

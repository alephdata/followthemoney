from csv import DictReader
from banal import is_listish


class Source(object):

    def __init__(self, query, data):
        self.query = query
        self.filters = query.data.get('filters', {}).items()
        self.filters_not = query.data.get('filters_not', {}).items()

    def __len__(self):
        return 0


class StreamSource(Source):

    def apply_filter(self, data, key, pred):
        value = data.get(key)
        if is_listish(pred):
            return value in pred
        return value == pred

    def check_filters(self, data):
        for (k, v) in self.filters:
            if not self.apply_filter(data, k, v):
                return False
        for (k, v) in self.filters_not:
            if self.apply_filter(data, k, v):
                return False
        return True

    @classmethod
    def read_csv(cls, fh):
        for row in DictReader(fh, skipinitialspace=True):
            yield row

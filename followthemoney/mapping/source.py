from csv import DictReader


class Source(object):

    def __init__(self, query, data):
        self.query = query
        self.filters = query.data.get('filters', {}).items()
        self.filters_not = query.data.get('filters_not', {}).items()

    def __len__(self):
        return 0


class StreamSource(Source):

    def check_filters(self, data):
        for (k, v) in self.filters:
            if v != data.get(k):
                return False
        for (k, v) in self.filters_not:
            if v == data.get(k):
                return False
        return True

    @classmethod
    def read_csv(cls, fh):
        for row in DictReader(fh, skipinitialspace=True):
            yield row

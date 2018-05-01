

class Source(object):

    def __init__(self, query, data):
        self.query = query
        self.filters = query.data.get('filters', {}).items()
        self.filters_not = query.data.get('filters_not', {}).items()

    def __len__(self):
        return 0

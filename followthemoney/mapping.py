import six


class QueryTable(object):
    """A table to be joined in."""

    def __init__(self, query, data):
        self.query = query
        if isinstance(data, six.string_types):
            data = {'table': data}
        self.data = data
        self.table_ref = data.get('table')
        self.alias_ref = data.get('alias', self.table_ref)
        self.table = Table(self.table_ref, self.query.meta, autoload=True)
        self.alias = self.table.alias(self.alias_ref)

        self.refs = {}
        for column in self.alias.columns:
            name = '%s.%s' % (self.alias_ref, column.name)
            labeled_column = column.label('col_%s' % uuid4().get_hex()[:10])
            self.refs[name] = labeled_column
            self.refs[column.name] = labeled_column

    def __repr__(self):
        return '<QueryTable(%r,%r)>' % (self.alias_ref, self.table_ref)


class QueryMapping(object):
    """A dataset describes one set of data to be loaded."""

    def __init__(self, collection, data):
        self.collection = collection
        self.roles = collection.roles
        self.data = data

        self.entities = []
        for ename, edata in data.get('entities').items():
            self.entities.append(EntityMapper(self, ename, edata))

        self.links = []
        for ldata in data.get('links', []):
            self.links.append(LinkMapper(self, ldata))

    @property
    def active_refs(self):
        refs = set()
        for item in self.entities + self.links:
            for ref in item.refs:
                refs.add(ref)
        return refs

    def __repr__(self):
        return '<Query(%s)>' % self.collection.foreign_id


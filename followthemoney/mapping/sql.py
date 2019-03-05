import os
import six
import logging
from uuid import uuid4
from banal import ensure_list, is_listish
from normality import stringify
from sqlalchemy import create_engine, MetaData
from sqlalchemy import select, func
# from sqlalchemy import text as sql_text
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import Table

from followthemoney.mapping.source import Source
from followthemoney.exc import InvalidMapping

log = logging.getLogger(__name__)
DATA_PAGE = 1000


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
            labeled_column = column.label('col_%s' % uuid4().hex[:10])
            self.refs[name] = labeled_column
            self.refs[column.name] = labeled_column


class SQLSource(Source):
    """Query mapper for loading data from a SQL query."""

    def __init__(self, query, data):
        super(SQLSource, self).__init__(query, data)
        self.database_uri = os.path.expandvars(data.get('database'))
        kwargs = {}
        if self.database_uri.lower().startswith('postgres'):
            kwargs['server_side_cursors'] = True
        self.engine = create_engine(self.database_uri,
                                    poolclass=NullPool,
                                    **kwargs)
        self.meta = MetaData()
        self.meta.bind = self.engine

        tables = ensure_list(data.get('table'))
        tables.extend(ensure_list(data.get('tables')))
        self.tables = [QueryTable(self, f) for f in tables]
        self.joins = ensure_list(data.get('joins'))

    def get_column(self, ref):
        for table in self.tables:
            if ref in table.refs:
                return table.refs.get(ref)
        raise InvalidMapping("Missing reference: %s" % ref)

    def apply_filters(self, q):
        for col, val in self.filters:
            if is_listish(val):
                q = q.where(self.get_column(col).in_(val))
            else:
                q = q.where(self.get_column(col) == val)
        for col, val in self.filters_not:
            if is_listish(val):
                q = q.where(self.get_column(col).notin_(val))
            else:
                q = q.where(self.get_column(col) != val)
        # not sure this is a great idea:
        # if self.data.get('where'):
        #    q = q.where(sql_text(self.data.get('where')))
        for join in self.joins:
            left = self.get_column(join.get('left'))
            right = self.get_column(join.get('right'))
            q = q.where(left == right)
        return q

    def compose_query(self):
        from_clause = [t.alias for t in self.tables]
        columns = [self.get_column(r) for r in self.query.refs]
        q = select(columns=columns, from_obj=from_clause, use_labels=True)
        return self.apply_filters(q)

    @property
    def records(self):
        """Compose the actual query and return an iterator of ``Record``."""
        mapping = [(r, self.get_column(r).name) for r in self.query.refs]
        q = self.compose_query()
        log.info("Query: %s", q)
        rp = self.engine.execute(q)
        while True:
            rows = rp.fetchmany(size=DATA_PAGE)
            if not len(rows):
                break
            for row in rows:
                data = {}
                for ref, name in mapping:
                    data[ref] = stringify(row[name])
                yield data

    def __len__(self):
        from_clause = [t.alias for t in self.tables]
        columns = [func.count('*')]
        q = select(columns=columns, from_obj=from_clause, use_labels=True)
        q = self.apply_filters(q)
        rp = self.engine.execute(q)
        return rp.scalar()

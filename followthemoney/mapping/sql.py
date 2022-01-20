import os
import logging
from uuid import uuid4
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Union, cast
from banal import ensure_list, is_listish, keys_values
from sqlalchemy import create_engine, MetaData
from sqlalchemy import select, func
from sqlalchemy.sql.elements import Label
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import Table
from sqlalchemy.sql.expression import Select

from followthemoney.mapping.source import Record, Source
from followthemoney.util import sanitize_text
from followthemoney.exc import InvalidMapping

if TYPE_CHECKING:
    from followthemoney.mapping.query import QueryMapping


log = logging.getLogger(__name__)
DATA_PAGE = 1000


class QueryTable(object):
    """A table to be joined in."""

    def __init__(self, meta: MetaData, data: Union[str, Dict[str, str]]) -> None:
        if isinstance(data, str):
            data = {"table": data}
        table_ref = data.get("table")
        if table_ref is None:
            raise InvalidMapping("Query has no table!")
        alias_ref = data.get("alias", table_ref)
        self.table = Table(table_ref, meta, autoload=True)
        self.alias = self.table.alias(alias_ref)

        self.refs: Dict[str, Label[Any]] = {}
        for column in self.alias.columns:
            name = "%s.%s" % (alias_ref, column.name)
            labeled_column = column.label("col_%s" % uuid4().hex[:10])
            self.refs[name] = labeled_column
            self.refs[column.name] = labeled_column


class SQLSource(Source):
    """Query mapper for loading data from a SQL query."""

    def __init__(self, query: "QueryMapping", data: Dict[str, Any]) -> None:
        super(SQLSource, self).__init__(query, data)
        database = data.get("database")
        if database is None:
            raise InvalidMapping("No database in SQL mapping!")
        self.database_uri = cast(str, os.path.expandvars(database))
        kwargs = {}
        if self.database_uri.lower().startswith("postgres"):
            kwargs["server_side_cursors"] = True
        self.engine = create_engine(self.database_uri, poolclass=NullPool, **kwargs)  # type: ignore
        self.meta = MetaData()
        self.meta.bind = self.engine

        tables = keys_values(data, "table", "tables")
        self.tables = [QueryTable(self.meta, f) for f in tables]
        self.joins = cast(List[Dict[str, str]], ensure_list(data.get("joins")))

    def get_column(self, ref: Optional[str]) -> Label[Any]:
        for table in self.tables:
            if ref in table.refs:
                return table.refs[ref]
        raise InvalidMapping("Missing reference: %s" % ref)

    def apply_filters(self, q: Select) -> Select:
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
            left = self.get_column(join.get("left"))
            right = self.get_column(join.get("right"))
            q = q.where(left == right)
        return q

    def compose_query(self) -> Select:
        from_clause = [t.alias for t in self.tables]
        columns = [self.get_column(r) for r in self.query.refs]
        q = select(columns=columns, from_obj=from_clause, use_labels=True)
        return self.apply_filters(q)

    @property
    def records(self) -> Generator[Record, None, None]:
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
                data: Record = {}
                for ref, name in mapping:
                    value = sanitize_text(row[name])
                    if value is not None:
                        data[ref] = value
                yield data

    def __len__(self) -> int:
        from_clause = [t.alias for t in self.tables]
        columns = [func.count("*")]
        q = select(columns=columns, from_obj=from_clause, use_labels=True)
        q = self.apply_filters(q)
        rp = self.engine.execute(q)
        return int(rp.scalar())

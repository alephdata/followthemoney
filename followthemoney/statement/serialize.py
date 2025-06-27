import csv
import click
import orjson
from io import TextIOWrapper
from pathlib import Path
from types import TracebackType
from typing import cast
from typing import BinaryIO, Generator, Iterable, List, Optional, TextIO, Type
from rigour.boolean import text_bool

from followthemoney.statement.statement import Statement, StatementDict
from followthemoney.statement.util import unpack_prop


JSON = "json"
CSV = "csv"
PACK = "pack"
FORMATS = [JSON, CSV, PACK]

CSV_BATCH = 5000
CSV_COLUMNS = [
    "canonical_id",
    "entity_id",
    "prop",
    "prop_type",
    "schema",
    "value",
    "dataset",
    "lang",
    "original_value",
    "external",
    "first_seen",
    "last_seen",
    "origin",
    "id",
]


def read_json_statements(
    fh: BinaryIO,
    max_line: int = 40 * 1024 * 1024,
) -> Generator[Statement, None, None]:
    while line := fh.readline(max_line):
        data = orjson.loads(line)
        yield Statement.from_dict(data)


def read_csv_statements(fh: BinaryIO) -> Generator[Statement, None, None]:
    wrapped = TextIOWrapper(fh, encoding="utf-8")
    for row in csv.DictReader(wrapped, dialect=csv.unix_dialect):
        data = cast(StatementDict, row)
        data["external"] = text_bool(row.get("external")) or False
        if row.get("lang") == "":
            data["lang"] = None
        if row.get("original_value") == "":
            data["original_value"] = None
        yield Statement.from_dict(data)


def read_pack_statements(fh: BinaryIO) -> Generator[Statement, None, None]:
    wrapped = TextIOWrapper(fh, encoding="utf-8")
    yield from read_pack_statements_decoded(wrapped)


def read_pack_statements_decoded(fh: TextIO) -> Generator[Statement, None, None]:
    for row in csv.reader(fh, dialect=csv.unix_dialect):
        (
            entity_id,
            prop,
            value,
            dataset,
            lang,
            original,
            _,
            external,
            first_seen,
            last_seen,
        ) = row[:10]
        schema, _, prop = unpack_prop(prop)
        yield Statement(
            entity_id=entity_id,
            prop=prop,
            schema=schema,
            value=value,
            dataset=dataset,
            lang=lang or None,
            original_value=original or None,
            first_seen=first_seen,
            external=external == "t",
            canonical_id=entity_id,
            last_seen=last_seen,
        )


def read_statements(fh: BinaryIO, format: str) -> Generator[Statement, None, None]:
    if format == CSV:
        yield from read_csv_statements(fh)
    elif format == PACK:
        yield from read_pack_statements(fh)
    else:
        yield from read_json_statements(fh)


def read_path_statements(path: Path, format: str) -> Generator[Statement, None, None]:
    if str(path) == "-":
        fh = click.get_binary_stream("stdin")
        yield from read_statements(fh, format=format)
        return
    with open(path, "rb") as fh:
        yield from read_statements(fh, format=format)


def get_statement_writer(fh: BinaryIO, format: str) -> "StatementWriter":
    if format == CSV:
        wrapped = TextIOWrapper(fh, encoding="utf-8")
        return CSVStatementWriter(wrapped)
    elif format == PACK:
        wrapped = TextIOWrapper(fh, encoding="utf-8")
        return PackStatementWriter(wrapped)
    elif format == JSON:
        return JSONStatementWriter(fh)
    raise RuntimeError("Unknown statement format: %s" % format)


def write_statements(
    fh: BinaryIO, format: str, statements: Iterable[Statement]
) -> None:
    writer = get_statement_writer(fh, format)
    for stmt in statements:
        writer.write(stmt)
    writer.close()


class StatementWriter(object):
    def write(self, stmt: Statement) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    def __enter__(self) -> "StatementWriter":
        return self

    def __exit__(
        self,
        type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close()


class JSONStatementWriter(StatementWriter):
    def __init__(self, fh: BinaryIO) -> None:
        self.fh = fh

    def write(self, stmt: Statement) -> None:
        data = stmt.to_dict()
        out = orjson.dumps(data, option=orjson.OPT_APPEND_NEWLINE)
        self.fh.write(out)

    def close(self) -> None:
        self.fh.close()


class CSVStatementWriter(StatementWriter):
    def __init__(self, fh: TextIO) -> None:
        self.fh = fh
        self.writer = csv.writer(self.fh, dialect=csv.unix_dialect)
        self.writer.writerow(CSV_COLUMNS)
        self._batch: List[List[Optional[str]]] = []

    def write(self, stmt: Statement) -> None:
        row = stmt.to_csv_row()
        self._batch.append([row[c] for c in CSV_COLUMNS])
        if len(self._batch) >= CSV_BATCH:
            self.writer.writerows(self._batch)
            self._batch.clear()

    def close(self) -> None:
        if len(self._batch) > 0:
            self.writer.writerows(self._batch)
        self.fh.close()


class PackStatementWriter(StatementWriter):
    def __init__(self, fh: TextIO) -> None:
        self.fh = fh
        self.writer = csv.writer(
            self.fh,
            dialect=csv.unix_dialect,
            quoting=csv.QUOTE_MINIMAL,
        )
        self._batch: List[List[Optional[str]]] = []

    def write(self, stmt: Statement) -> None:
        # HACK: This is very similar to the CSV writer, but at the very inner
        # loop of the application, so we're duplicating code here.
        row = [
            stmt.entity_id,
            f"{stmt.schema}:{stmt.prop}",
            stmt.value,
            stmt.dataset,
            stmt.lang,
            stmt.original_value,
            None,
            "t" if stmt.external else None,
            stmt.first_seen,
            stmt.last_seen,
        ]
        self._batch.append(row)
        if len(self._batch) >= CSV_BATCH:
            self.writer.writerows(self._batch)
            self._batch.clear()

    def close(self) -> None:
        if len(self._batch) > 0:
            self.writer.writerows(self._batch)
        self.fh.close()

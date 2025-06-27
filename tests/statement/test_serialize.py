from pathlib import Path
from tempfile import TemporaryDirectory

from followthemoney.dataset import DefaultDataset
from followthemoney.statement.entity import StatementEntity
from followthemoney.statement import Statement, write_statements
from followthemoney.statement import read_path_statements
from followthemoney.statement.serialize import CSV, JSON, PACK


EXAMPLE = {
    "id": "bla",
    "schema": "Person",
    "properties": {"name": ["John Doe"], "birthDate": ["1976"]},
}


def test_json_statements():
    with TemporaryDirectory() as tmpdir:
        entity = StatementEntity.from_data(DefaultDataset, EXAMPLE)
        path = Path(tmpdir) / "statement.json"
        with open(path, "wb") as fh:
            write_statements(fh, JSON, entity.statements)
        stmts = list(read_path_statements(path, JSON))
        assert len(stmts) == 3
        for stmt in stmts:
            assert stmt.canonical_id == "bla", stmt
            assert stmt.entity_id == "bla", stmt
            assert stmt.schema == "Person", stmt


def test_csv_statements():
    with TemporaryDirectory() as tmpdir:
        entity = StatementEntity.from_data(DefaultDataset, EXAMPLE)
        path = Path(tmpdir) / "statement.csv"
        with open(path, "wb") as fh:
            write_statements(fh, CSV, entity.statements)
        stmts = list(read_path_statements(path, CSV))
        assert len(stmts) == 3, stmts
        for stmt in stmts:
            assert stmt.canonical_id == "bla", stmt
            assert stmt.entity_id == "bla", stmt
            assert stmt.schema == "Person", stmt


def test_pack_statements():
    with TemporaryDirectory() as tmpdir:
        entity = StatementEntity.from_data(DefaultDataset, EXAMPLE)
        path = Path(tmpdir) / "statement.pack"
        with open(path, "wb") as fh:
            write_statements(fh, PACK, entity.statements)
        stmts = list(read_path_statements(path, PACK))
        assert len(stmts) == 3, stmts
        for stmt in stmts:
            assert stmt.canonical_id == "bla", stmt
            assert stmt.entity_id == "bla", stmt
            assert stmt.schema == "Person", stmt


def test_statement_db_row_roundtrip():
    class MockRow(dict):
        def __getattr__(self, item):
            try:
                return self[item]
            except KeyError:
                raise AttributeError(item)

    EXAMPLE_2 = {
        "id": "bla",
        "schema": "Person",
        "properties": {"name": ["John Doe"], "birthDate": ["1976"]},
    }
    sp = StatementEntity.from_data(DefaultDataset, EXAMPLE_2)
    statements = [Statement.from_dict(s) for s in sp.to_statement_dict()["statements"]]
    db_rows_dicts = [stmt.to_db_row() for stmt in statements]
    db_rows = [MockRow(row) for row in db_rows_dicts]
    roundtrip_statements = [Statement.from_db_row(row) for row in db_rows]
    for stmt in roundtrip_statements:
        assert stmt.canonical_id == "bla", stmt
        assert stmt.entity_id == "bla", stmt
        assert stmt.schema == "Person", stmt

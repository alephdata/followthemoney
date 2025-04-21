import pytest
from rigour.time import utc_now
from typing import Any, Dict, List

from followthemoney.types import registry
from followthemoney.exc import InvalidData
from followthemoney.dataset import Dataset
from followthemoney.statement.entity import CompositeEntity
from followthemoney.statement.statement import Statement

DAIMLER = "66ce9f62af8c7d329506da41cb7c36ba058b3d28"
EXAMPLE = {
    "id": "bla",
    "schema": "Person",
    "properties": {"name": ["John Doe"], "birthDate": ["1976"]},
}


def test_donations_entities(donations_json: List[Dict[str, Any]]):
    dx = Dataset.make({"name": "test", "title": "Test"})
    for data in donations_json:
        sp = CompositeEntity.from_data(dx, data)
        assert sp.schema is not None
        assert sp.id is not None
        assert len(sp) > 0


def test_example_entity():
    dx = Dataset.make({"name": "test", "title": "Test"})
    sp = CompositeEntity.from_data(dx, EXAMPLE)
    assert len(sp) == 3
    idstmt = list(sp.statements)[-1]
    assert idstmt.value == "836baf194d59a68c4092e208df30134800c732cc"
    assert sp.caption == "John Doe"
    assert "John Doe", sp.get_type_values(registry.name)
    sp.add("country", "us")
    assert len(sp) == 4
    idstmt = list(sp.statements)[-1]
    assert idstmt.value == "c3aec8e1fcd86bc55171917db7c993d6f3ad5fe0"
    sp.add("country", {"gb"})
    assert len(sp) == 5
    sp.add("country", ("gb", "us"))
    assert len(sp) == 5
    sp.add("country", ["gb", "us"])
    assert len(sp) == 5
    sp.set("country", "gb")
    assert len(sp) == 4
    data = sp.to_dict()
    assert data["id"] == sp.id, data
    idstmt = list(sp.statements)[-1]
    so = sp.clone()
    assert so.id == sp.id
    assert so.dataset == sp.dataset
    idstmt2 = list(so.statements)[-1]
    assert idstmt.value == idstmt2.value

    sx = CompositeEntity.from_statements(dx, sp.statements)
    assert sx.id == sp.id
    assert len(sx) == len(sp)

    sp.add("notes", "Ich bin eine banane!", lang="deu")
    claim = sp.get_statements("notes")[0]
    assert claim.lang == "deu", claim

    sp.add("banana", "Ich bin eine banane!", lang="deu", quiet=True)

    assert len(sp.get_statements("notes")) == 1
    sp.add("notes", None, lang="deu", quiet=True)
    assert len(sp.get_statements("notes")) == 1

    sp.add("alias", "Banana Boy")
    assert len(sp.get_statements("alias")) == 1

    sp.add("nationality", "Germany")
    claim = sp.get_statements("nationality")[0]
    assert claim.value == "de", claim
    assert claim.prop == "nationality", claim
    assert claim.prop_type == "country", claim
    assert claim.original_value == "Germany", claim

    for prop, val in sp.itervalues():
        if prop.name == "nationality":
            assert val == "de"

    pre_len = len(sp)
    sp.add("nationality", "de")
    sp.add("nationality", "it")
    sp.add("nationality", "fr")
    assert pre_len + 2 == len(sp), sp._statements["country"]
    assert len(sp.get_type_values(registry.country)) == 4

    sp.remove("nationality", "it")
    assert len(sp.get("nationality")) == 2
    sp.pop("nationality")
    assert len(sp.get("nationality")) == 0

    stmts = list(sp.statements)
    assert len(stmts) == len(sp), stmts
    assert sorted(stmts)[0].prop == Statement.BASE


def test_other_entity():
    dx = Dataset.make({"name": "test", "title": "Test"})
    smt = Statement(
        entity_id="blubb",
        prop="name",
        schema="LegalEntity",
        value="Jane Doe",
        dataset="test",
    )
    sp = CompositeEntity.from_statements(dx, [smt])
    assert sp.id == "blubb"
    assert sp.schema.name == "LegalEntity"
    assert "test" in sp.datasets
    assert sp.first_seen is None

    dt = utc_now()
    smt2 = Statement(
        entity_id="gnaa",
        prop="birthDate",
        schema="Person",
        value="1979",
        dataset="source",
        first_seen=dt,
    )
    sp.add_statement(smt2)
    assert sp.id == "blubb"
    assert sp.schema.name == "Person"
    assert sp.first_seen == dt

    with pytest.raises(InvalidData):
        smt2 = Statement(
            entity_id="gnaa",
            prop="incorporationDate",
            schema="Company",
            value="1979",
            dataset="source",
        )
        sp.add_statement(smt2)

    with pytest.raises(InvalidData):
        sp.add("identification", "abc")
    sp.add("identification", "abc", quiet=True)

    sp.add("alias", "Harry", lang="deu")
    aliases = sp.get_statements("alias")
    assert aliases[0].lang == "deu", aliases

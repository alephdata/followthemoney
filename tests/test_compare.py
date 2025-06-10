import pytest
from copy import deepcopy

from followthemoney import model
from followthemoney.compare import compare, compare_names


ENTITY = {
    "id": "test",
    "schema": "Person",
    "properties": {
        "name": ["Ralph Tester"],
        "birthDate": ["1972-05-01"],
        "idNumber": ["9177171", "8e839023"],
        "topics": ["role.spy"],
    },
}


def test_compare_names():
    left = {"schema": "Person", "properties": {"name": ["mr frank banana"]}}
    left = model.get_proxy(left)
    right = {
        "schema": "Person",
        "properties": {"name": ["mr frank bananoid"]},
    }
    right = model.get_proxy(right)
    same_score = compare_names(left.schema, left, left)
    assert same_score > 0.5, same_score
    lr_score = compare_names(left.schema, left, right)
    assert lr_score > 0.1, lr_score
    assert lr_score < same_score, (lr_score, same_score)


def test_compare_countries():
    left = model.get_proxy(
        {
            "schema": "Person",
            "properties": {"name": ["Frank Banana"], "nationality": ["ie"]},
        }
    )
    no_country = model.get_proxy(
        {"schema": "Person", "properties": {"name": ["Frank Banana"]}}
    )
    baseline = compare(left, no_country)
    assert compare(left, left) > baseline


def test_compare_basic():
    entity = model.get_proxy(ENTITY)
    best_score = compare(entity, entity)
    assert best_score > 0.5, best_score
    comp = model.get_proxy({"schema": "RealEstate"})
    assert compare(entity, comp) == pytest.approx(0)
    assert compare(comp, comp) == pytest.approx(0)

    comp = model.get_proxy({"schema": "Person"})
    assert compare(entity, comp) == pytest.approx(0)

    comp = model.get_proxy({"schema": "LegalEntity"})
    assert compare(entity, comp) == pytest.approx(0)


def test_compare_quality():
    entity = model.get_proxy(ENTITY)
    best_score = compare(entity, entity)
    reduced = deepcopy(ENTITY)
    reduced["properties"].pop("birthDate")
    reduced["properties"].pop("idNumber")
    reduced_proxy = model.get_proxy(reduced)
    assert compare(entity, reduced_proxy) < best_score

    reduced = deepcopy(ENTITY)
    reduced["properties"]["name"] = ["Frank Banana"]
    reduced_proxy = model.get_proxy(reduced)
    assert compare(entity, reduced_proxy) < best_score

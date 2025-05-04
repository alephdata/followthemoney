from followthemoney.types import registry

entities = registry.entity


def test_entity_parse():
    assert entities.clean("888") == "888"
    assert entities.clean(888) == "888"
    assert entities.clean({"id": 888}) == "888"
    assert entities.clean(None) is None
    assert entities.clean("With spaces") is None
    assert entities.clean("With-dash") == "With-dash"
    assert entities.clean("With!special") is None
    assert entities.clean("with.dot") == "with.dot"
    assert entities.clean("14") == "14"
    assert entities.clean(14) == "14"


def test_entity_funcs():
    assert entities.specificity("bla") == 1

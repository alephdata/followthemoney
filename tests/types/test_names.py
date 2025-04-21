from followthemoney.types import registry

names = registry.name


def test_repr():
    assert repr(names) == "<name>"


def test_parse():
    assert names.clean("Hans Well") == "Hans Well"
    assert names.clean("Hans   Well ") == "Hans Well"
    assert names.clean('"Hans Well"') == "Hans Well"


def test_pick():
    values = ["Banana", "banana", "nanana", "Batman"]
    assert names.pick(values) == "Banana"
    assert names.pick(["Banana"]) == "Banana"
    assert names.pick([]) is None

    values = ["Robert Smith", "Rob Smith", "Robert SMITH"]
    assert names.pick(values) == "Robert Smith"


def test_domain_validity():
    assert names.validate("huhu") is True
    assert names.validate("") is False


def test_specificity():
    assert names.specificity("bo") == 0
    assert names.specificity("boban") > 0

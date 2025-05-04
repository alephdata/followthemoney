from followthemoney.types import registry


def test_funcs():
    t = registry.name
    assert t.country_hint("banana") is None
    assert str(t) == "name"
    assert hash(t) == hash("name")

    assert t.compare_sets(["banana"], ["banana"]) > 0
    assert t.compare_sets(["banana"], []) == 0


def test_dict():
    data = registry.name.to_dict()
    assert data.get("label") == "Name"
    assert data.get("group") == "names"
    assert data.get("description", "").startswith(
        "A name used for a person or company."
    )


def test_string_cleaning():
    t = registry.string
    assert t.clean("₸15,000,000").startswith("₸")

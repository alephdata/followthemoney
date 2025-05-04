from followthemoney.types import registry


def test_registry():
    assert registry.entity == registry.get("entity")
    assert registry.get("banana") is None
    assert registry.get(registry.entity) == registry.entity

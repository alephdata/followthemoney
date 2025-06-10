import pytest
from followthemoney.types import registry


def test_registry():
    assert registry.entity == registry.get("entity")
    with pytest.raises(AttributeError):
        registry.get("banana")
    assert registry.entity in registry.pivots
    assert registry.string not in registry.pivots
    assert registry.entity in registry.matchable
    assert registry.string not in registry.matchable
    assert registry.entity in registry.types
    assert registry.string in registry.types
    assert "entities" in registry.groups

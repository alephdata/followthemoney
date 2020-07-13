from unittest import TestCase
from followthemoney.util import merge_context


class UtilTestCase(TestCase):
    def test_merge_value(self):
        old = {
            "foo": "bar",
        }
        new = {
            "foo": "quux",
        }
        result = merge_context(old, new)
        assert result["foo"] == ["bar", "quux"], result

    def test_merge_different(self):
        old = {
            "foo": "quux",
        }
        new = {
            "bar": "quux",
        }
        result = merge_context(old, new)
        assert result["foo"] == ["quux"], result
        assert result["bar"] == ["quux"], result

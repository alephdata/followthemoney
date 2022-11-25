import unittest

from followthemoney.types import registry


class CommonTest(unittest.TestCase):
    def test_funcs(self):
        t = registry.name
        self.assertEqual(t.country_hint("banana"), None)
        self.assertEqual(str(t), "name")
        self.assertEqual(hash(t), hash("name"))

        self.assertGreater(t.compare_sets(["banana"], ["banana"]), 0)
        self.assertEqual(t.compare_sets(["banana"], []), 0)

    def test_dict(self):
        data = registry.name.to_dict()
        assert data.get("label") == "Name"
        assert data.get("group") == "names"
        assert data.get("description", "").startswith("A name used for a person or company.")

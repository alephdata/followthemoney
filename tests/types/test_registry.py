import unittest

from followthemoney.types import registry


class RegistryTest(unittest.TestCase):

    def test_registry(self):
        assert registry.entity == registry.get('entity')
        assert registry.get('banana') is None
        assert registry.get(registry.entity) == registry.entity

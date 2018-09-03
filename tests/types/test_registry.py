import unittest

from followthemoney.types import registry


class RegistryTest(unittest.TestCase):

    def test_ref(self):
        assert registry.entity == registry.get('entity')
        assert registry.get('banana') is None
        assert registry.entity.ref('banana') == 'e:banana'
        t, v = registry.deref('e:banana')
        assert t == registry.entity
        assert v == 'banana'

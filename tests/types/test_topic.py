import unittest

from followthemoney.types import registry


class TopicsTest(unittest.TestCase):

    def test_country_codes(self):
        topics = registry.topic
        self.assertEqual(topics.clean('role.pep'), 'role.pep')
        self.assertEqual(topics.clean('role.PEP'), 'role.pep')
        self.assertEqual(topics.clean('banana'), None)
        self.assertEqual(topics.clean(None), None)
        self.assertTrue(topics.validate('role.pep'))
        self.assertTrue(topics.validate('role.PEP'))
        self.assertFalse(topics.validate('DEU'))
        self.assertFalse(topics.validate(''))
        self.assertFalse(topics.validate(None))
        assert 'ftm:topic:role.pep' in topics.rdf('role.pep')

import unittest

from followthemoney.types import registry

json = registry.json


class JsonTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(json.clean('88'), '88')
        self.assertEqual(json.clean({'id': 88}), json.pack({'id': 88}))
        self.assertEqual(json.clean(None), None)

    def test_unpack(self):
        data = json.clean({'id': 88})
        self.assertEqual(json.unpack(data)['id'], 88)
        self.assertEqual(json.unpack(None), None)
        self.assertEqual(json.unpack("[x]"), "[x]")

    def test_normalize(self):
        self.assertEqual(json.normalize('FOO'), ['FOO'])
        self.assertEqual(json.normalize(None), [])

    def test_join(self):
        # Pretty weird behaviour, but hey:
        data = json.pack({'id': 88})
        joined = json.join([data, data, data])
        joined = json.unpack(joined)
        self.assertEqual(joined[0]['id'], 88)

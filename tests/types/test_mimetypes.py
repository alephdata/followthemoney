import unittest

from followthemoney.types import registry

mimetypes = registry.mimetype


class MimetypesTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(mimetypes.clean(''), None)

    def test_normalize(self):
        self.assertEqual(mimetypes.normalize('text/PLAIN'), ['text/plain'])
        self.assertEqual(mimetypes.normalize(' '), [])

    def test_base(self):
        self.assertEqual(str(mimetypes.rdf('text/plain')),
                         'urn:mimetype:text/plain')
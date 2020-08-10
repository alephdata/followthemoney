import unittest

from followthemoney.types import registry

mimetypes = registry.mimetype


class MimetypesTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(mimetypes.clean(""), None)
        self.assertEqual(mimetypes.clean(" "), None)
        self.assertEqual(mimetypes.clean("text/PLAIN"), "text/plain")

    def test_base(self):
        self.assertEqual(str(mimetypes.rdf("text/plain")), "urn:mimetype:text/plain")

import unittest

from followthemoney.types import urls


class UrlsTest(unittest.TestCase):

    def test_is_url(self):
        self.assertTrue(urls.validate('http://foo.org'))
        self.assertFalse(urls.validate(None))
        self.assertFalse(urls.validate('hello'))

    def test_parse_url(self):
        self.assertEqual(urls.clean('http://foo.com'), 'http://foo.com/')
        self.assertEqual(urls.clean('http://foo.com/#lala'), 'http://foo.com/')

        self.assertEqual(urls.clean('http://foo.com?b=1&a=2'),
                         'http://foo.com/?a=2&b=1')
        self.assertEqual(urls.clean('http://FOO.com'), 'http://foo.com/')
        self.assertEqual(urls.clean('http://FOO.com/A'), 'http://foo.com/A')

    def test_specificity(self):
        self.assertEqual(urls.specificity('http://foo.com/'), 1)

import unittest

from followthemoney.types import registry

urls = registry.url


class UrlsTest(unittest.TestCase):

    def test_is_url(self):        
        self.assertTrue(urls.validate('http://foo.org'))
        self.assertFalse(urls.validate(None))
        self.assertFalse(urls.validate('hello'))

    def test_unicode_url(self):
        utext = 'http://ko.wikipedia.org/wiki/위키백과:대문'
        self.assertTrue(urls.validate(utext))
        self.assertFalse(urls.validate(utext.encode('euc-kr')))

    def test_parse_url(self):
        self.assertEqual(urls.clean('http://foo.com'), 'http://foo.com/')
        self.assertEqual(urls.clean('http://foo.com/#lala'), 'http://foo.com/')

        self.assertEqual(urls.clean('http://foo.com?b=1&a=2'),
                         'http://foo.com/?a=2&b=1')
        self.assertEqual(urls.clean('http://FOO.com'), 'http://foo.com/')
        self.assertEqual(urls.clean('http://FOO.com/A'), 'http://foo.com/A')

    def test_specificity(self):
        self.assertEqual(urls.specificity('http://foo.com/'), 1)

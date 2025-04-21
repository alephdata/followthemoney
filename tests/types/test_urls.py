from followthemoney.types import registry

urls = registry.url


def test_is_url():
    assert urls.validate("http://foo.org")
    assert not urls.validate(None)
    assert not urls.validate("hello")
    assert urls.validate("foo.org")
    assert urls.validate("//foo.org")


def test_unicode_url():
    utext = "http://ko.wikipedia.org/wiki/위키백과:대문"
    assert urls.validate(utext)
    assert urls.validate(utext.encode("utf-8"))


def test_parse_url():
    assert urls.clean("http://foo.com/") == "http://foo.com/"
    assert urls.clean("http://foo.com/#lala") == "http://foo.com/#lala"
    assert urls.clean("http://foo.com?b=1&a=2") == "http://foo.com/?b=1&a=2"
    assert urls.clean("http://FOO.com") == "http://FOO.com/"
    assert urls.clean("http://FOO.com/A") == "http://FOO.com/A"


def test_specificity():
    assert urls.specificity("http://foo.com/#banana") > 0.1

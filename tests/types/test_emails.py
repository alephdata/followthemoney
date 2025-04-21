from followthemoney.types import registry

emails = registry.email


def test_email_parse():
    assert emails.clean("foo@pudo.org") == "foo@pudo.org"
    assert emails.clean('"foo@pudo.org"') == "foo@pudo.org"
    assert emails.clean("pudo.org") is None
    assert emails.clean("@pudo.org") is None
    assert emails.clean("foo@") is None
    assert emails.clean(None) is None
    assert emails.clean(5) is None
    assert emails.clean("foo@PUDO.org") == "foo@pudo.org"
    assert emails.clean("FOO@PUDO.org") == "FOO@pudo.org"
    assert (
        emails.clean(
            "foo@0123456789012345678901234567890123456789012345678901234567890.example.com"
        )
        == "foo@0123456789012345678901234567890123456789012345678901234567890.example.com"
    )
    assert (
        emails.clean(
            "foo@0123456789012345678901234567890123456789012345678901234567890123.example.com"
        )
        is None
    )


def test_domain_validity():
    assert emails.validate("foo@pudo.org") is True
    assert emails.validate("foo@pudo") is False
    assert emails.validate(None) is False
    assert emails.validate("") is False
    assert emails.validate("@pudo.org") is False
    assert emails.validate("foo@") is False


def test_specificity():
    assert emails.specificity("foo@pudo.org") == 1

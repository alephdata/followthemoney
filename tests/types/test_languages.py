from followthemoney.types import registry


def test_language_validate():
    languages = registry.language
    assert languages.validate("deu") is True
    assert languages.validate("eng") is True
    assert languages.validate("us") is False
    assert languages.validate("") is False
    assert languages.validate(None) is False


def test_language_clean():
    languages = registry.language
    assert languages.clean("deu") == "deu"
    assert languages.clean("de") == "deu"
    assert languages.clean("xx") is None
    assert languages.clean(None) is None


def test_language_funcs():
    languages = registry.language
    assert len(languages.names) > 1
    assert languages.node_id("deu") == "language:deu"
    assert languages.specificity("deu") == 0

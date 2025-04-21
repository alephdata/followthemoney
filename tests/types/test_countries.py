from followthemoney.types import registry


def test_country_codes():
    countries = registry.country
    assert countries.clean("DE") == "de"
    assert countries.validate("DE")
    assert not countries.validate("DEU")
    assert not countries.validate("")
    assert not countries.validate(None)
    assert not countries.validate(4)
    assert not countries.validate("SU")
    assert countries.validate("XK")
    assert countries.validate("EU")

    assert countries.country_hint("eu") == "eu"
    assert "iso-3166:eu" in countries.rdf("eu")


def test_country_names():
    countries = registry.country
    assert countries.clean(None) is None
    assert countries.clean("Takatukaland", fuzzy=False) is None
    assert countries.clean("Germany") == "de"
    # assert countries.clean('Germani') == 'de'
    assert countries.clean("Soviet Union") == "suhh"

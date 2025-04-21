from followthemoney.types import registry


def test_topic_country_codes():
    topics = registry.topic
    assert topics.clean("role.pep") == "role.pep"
    assert topics.clean("role.PEP") == "role.pep"
    assert topics.clean("banana") is None
    assert topics.clean(None) is None
    assert topics.validate("role.pep") is True
    assert topics.validate("role.PEP") is True
    assert topics.validate("DEU") is False
    assert topics.validate("") is False
    assert topics.validate(None) is False
    assert "ftm:topic:role.pep" in topics.rdf("role.pep")

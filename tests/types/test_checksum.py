from followthemoney.types import registry


def test_rdf():
    csum = registry.checksum.rdf("00deadbeef")
    assert "hash:00deadbeef" in csum

from followthemoney.types import registry


def test_node_id():
    assert "checksum:00deadbeef" == registry.checksum.node_id("00deadbeef")

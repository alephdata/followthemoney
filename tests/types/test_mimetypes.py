from followthemoney.types import registry

mimetypes = registry.mimetype


def test_parse_mimetypes():
    assert mimetypes.clean("") is None
    assert mimetypes.clean(" ") is None
    assert mimetypes.clean("text/PLAIN") == "text/plain"


def test_base_mimetypes():
    assert mimetypes.node_id("text/plain") == "mimetype:text/plain"

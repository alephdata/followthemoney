from followthemoney.types import registry

json = registry.json


def test_json_parse():
    assert json.clean("88") == "88"
    assert json.clean({"id": 88}) == json.pack({"id": 88})
    assert json.clean(None) is None


def test_json_unpack():
    data = json.clean({"id": 88})
    assert json.unpack(data)["id"] == 88
    assert json.unpack(None) is None
    assert json.unpack("[x]") == "[x]"


def test_json_join():
    # Pretty weird behaviour, but hey:
    data = json.pack({"id": 88})
    joined = json.join([data, data, data])
    joined = json.unpack(joined)
    assert joined[0]["id"] == 88

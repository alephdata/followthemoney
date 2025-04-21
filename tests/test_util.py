from followthemoney.util import merge_context, join_text


def test_merge_value():
    old = {
        "foo": "bar",
    }
    new = {
        "foo": "quux",
    }
    result = merge_context(old, new)
    assert result["foo"] == ["bar", "quux"]


def test_merge_different():
    old = {
        "foo": "quux",
    }
    new = {
        "bar": "quux",
    }
    result = merge_context(old, new)
    assert result["foo"] == ["quux"]
    assert result["bar"] == ["quux"]


def test_join_text():
    text = join_text("hello", "", 3)
    assert text == "hello 3"
    text = join_text("hello", None, 3, sep="-")
    assert text == "hello-3"

from followthemoney import model
from followthemoney.namespace import Namespace


def test_basic():
    ns = Namespace.make("banana")
    assert Namespace.make(ns) == ns
    assert Namespace(b"banana") == ns
    assert "banana" in repr(ns), repr(ns)
    assert ns == Namespace("banana"), Namespace("banana")


def test_sign():
    ns = Namespace("banana")
    x = ns.sign("split")
    assert x.startswith("split"), x
    assert ns.sign(None) is None
    assert x.endswith(ns.signature("split"))
    assert ns.signature(None) is None


def test_sign_null():
    null = Namespace(None)
    assert null.sign("split") == "split", null.sign("split")
    assert null.signature("split") is None


def test_verify():
    ns = Namespace("banana")
    x = ns.sign("split")
    assert Namespace.SEP in x
    assert ns.verify(x)
    assert not ns.verify("split")
    assert not ns.verify(None)


def test_apply():
    entity = {
        "id": "banana",
        "schema": "LegalEntity",
        "properties": {"sameAs": ["kumkwat"], "parent": ["pretzel"]},
    }
    proxy = model.get_proxy(entity)
    assert proxy.id == "banana", proxy.id
    ns = Namespace("fruit")
    out = ns.apply(proxy)
    assert out.id == ns.sign(proxy.id), out
    # assert proxy.id in out.get('sameAs'), out

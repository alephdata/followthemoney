from followthemoney.types import registry

UK = """43 Duke Street
Edinburgh
EH6 8HH"""


def test_clean():
    addresses = registry.address
    assert addresses.clean(UK) == "43 Duke Street, Edinburgh, EH6 8HH"
    assert addresses.clean("huhu\n   haha") == "huhu, haha"
    assert addresses.clean("huhu,\n haha") == "huhu, haha"


def test_specificity():
    addresses = registry.address
    assert addresses.specificity(UK) > 0.2
    assert addresses.specificity("London") < 0.2

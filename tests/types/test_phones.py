from followthemoney import model
from followthemoney.types import registry


def test_us_number():
    phones = registry.phone
    assert phones.clean("+1-800-784-2433") == "+18007842433"
    assert phones.clean("+1 800 784 2433") == "+18007842433"
    assert phones.clean("+18007842433") == "+18007842433"
    assert phones.clean("+1 555 8379") is None

    assert phones.validate("+18007842433") is True
    assert phones.validate("banana") is False


def test_de_number():
    phones = registry.phone
    proxy = model.make_entity("Person")
    proxy.add("country", "DE")
    assert phones.clean("017623423980") is None
    assert phones.clean("017623423980", proxy=proxy) == "+4917623423980"


def test_specificity():
    phones = registry.phone
    assert phones.specificity("+4917623423980") == 1


def test_country_hint():
    phones = registry.phone
    assert phones.country_hint("+4917623423980") == "de"
    assert phones.country_hint(None) is None

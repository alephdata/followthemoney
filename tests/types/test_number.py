from followthemoney.types import registry

numbers = registry.number


def test_cast_numbers():
    assert numbers.to_number("1,00,000") == 100000.0
    assert numbers.to_number(" -999.0") == -999.0
    assert numbers.to_number("- 1,00,000.234") == -100000.234
    assert numbers.to_number("99") == 99.0
    assert numbers.to_number("banana") is None


def test_parse_numbers():
    assert numbers.parse("99") == ("99", None)
    assert numbers.parse("1,00,000") == ("100000", None)
    assert numbers.parse(" -999.0") == ("-999.0", None)
    assert numbers.parse("- 1,00,000.234") == ("-100000.234", None)
    assert numbers.parse("banana") == (None, None)
    assert numbers.parse("5 kg") == ("5", "kg")
    assert numbers.parse("5kg") == ("5", "kg")
    assert numbers.parse("42 °C") == ("42", "°C")


def test_format_numbers():
    assert numbers.caption("100000") == "100,000"
    assert numbers.caption("-999.0") == "-999"
    assert numbers.caption("-100000.234") == "-100,000.23"
    assert numbers.caption("-100000.234tonnes") == "-100,000.23 tonnes"
    assert numbers.caption("banana") == "banana"
    assert numbers.caption("1,00,000") == "100,000"

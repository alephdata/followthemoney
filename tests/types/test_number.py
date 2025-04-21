from followthemoney.types import registry

numbers = registry.number


def test_cast_numbers():
    assert numbers.to_number("1,00,000") == 100000.0
    assert numbers.to_number(" -999.0") == -999.0
    assert numbers.to_number("- 1,00,000.234") == -100000.234
    assert numbers.to_number("99") == 99.0
    assert numbers.to_number("banana") is None

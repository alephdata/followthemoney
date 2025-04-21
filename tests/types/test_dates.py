from datetime import datetime, timezone

from followthemoney.types import registry

dates = registry.date


def test_validate():
    assert dates.validate("2017-04-04T10:30:29")
    assert dates.validate("2017-04-04T10:30:29Z")
    assert dates.validate("2017-04-04T10:30:29+01")
    assert dates.validate("2017-04-04T10:30:29+0200")
    assert dates.validate("2017-04-04T10:30:29+03:00")
    assert dates.validate("2017-04-04T10:30:29-04:00")
    assert dates.validate(datetime.now(timezone.utc).isoformat())
    assert not dates.validate("01-02-2003")
    assert not dates.validate("Thursday 21 March 2017")


def test_is_partial_date():
    assert dates.validate("2017-04-04 10:30:29")
    assert dates.validate("2017-04-04 10:30")
    assert dates.validate("2017-04-04 10")
    assert dates.validate("2017-04-04")
    assert dates.validate("2017-4-4")
    assert dates.validate("2017-4")
    assert dates.validate("2017")
    assert not dates.validate("0017")
    assert not dates.validate(None)
    assert not dates.validate(5)
    assert not dates.validate("2017-20-01")


def test_chop_dates():
    assert dates.clean("2017-00-00") == "2017"
    assert dates.clean("2017-00-00T00:00:00") == "2017"
    assert dates.clean("2017-00-00T12:03:49") == "2017"
    assert dates.clean("2017-01-01T00:00:00") == "2017-01-01T00:00:00"


def test_patch_dates():
    assert dates.clean("2017-1-3") == "2017-01-03"
    assert dates.clean("2017-3") == "2017-03"
    assert dates.clean("2017-0") == "2017"
    assert dates.clean("2017-5-2T00:00:00") == "2017-05-02T00:00:00"
    assert dates.clean("2017-5-2T10:00:00") == "2017-05-02T10:00:00"


def test_convert_datetime():
    dt = datetime.now(timezone.utc)
    iso, _ = dt.isoformat().split(".", 1)
    assert dates.clean(dt) == iso
    assert dates.validate(iso)

    dt = datetime.now(timezone.utc)
    iso = dt.isoformat()[:19]
    assert dates.clean(dt) == iso


def test_parse_date():
    assert dates.clean(None) is None
    assert dates.clean("") is None
    assert dates.clean("banana") is None
    assert dates.clean("2017-04-04") == "2017-04-04"
    assert dates.clean("2017-4-4") == "2017-04-04"

    assert dates.clean("4/2017", format="%m/%Y") == "2017-04"
    assert dates.clean("4/2017", format="4/%Y") == "2017"
    assert dates.clean("4/2xx017", format="%m/%Y") is None


def test_specificity():
    assert dates.specificity("2011") == 0
    assert dates.specificity("2011-01-01") > 0.1


def test_compare():
    assert dates.compare("2011-01-01", "2011-01-01") > 0.9


def test_cast_num():
    assert dates.to_number("2017-04-04T10:30:29") == 1491301829.0
    assert dates.to_number("2017-04-04T10:30") == 1491301800.0
    assert dates.to_number("2017-04-04T10") == 1491300000.0
    assert dates.to_number("2017-04-04") == 1491264000.0
    assert dates.to_number("2017-4-4") == 1491264000.0
    assert dates.to_number("2017-4") == 1491004800.0
    assert dates.to_number("2017") == 1483228800.0

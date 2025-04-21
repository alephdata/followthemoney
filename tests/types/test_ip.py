from followthemoney.types import registry

ips = registry.ip


def test_ip_validate():
    assert ips.validate("172.16.254.1")
    assert not ips.validate("355.16.254.1")
    assert not ips.validate("16.254.1")
    assert not ips.validate("172.162541")
    assert not ips.validate(None)

    assert ips.validate("2001:db8:0:1234:0:567:8:1")
    assert not ips.validate("2001:zz8:0:1234:0:567:8:1")
    assert not ips.validate("20001:db8:0:1234:0:567:8:1")


def test_ip_clean():
    assert ips.clean("172.16.254.1") == "172.16.254.1"
    assert ips.clean(None) is None
    assert ips.clean("-1") is None


def test_funcs():
    assert str(ips.rdf("172.16.254.1")) == "ip:172.16.254.1"


def test_specificity():
    assert ips.specificity("172.16.254.1") == 1

import random
import string

from unittest import TestCase

from followthemoney import model
from followthemoney.multi_part_proxy import MultiPartProxy


ENTITY = {
    "id": "test",
    "schema": "Person",
    "properties": {
        "name": ["Ralph Tester"],
        "birthDate": ["1972-05-01"],
        "idNumber": ["9177171", "8e839023"],
        "website": ["https://ralphtester.me"],
        "phone": ["+12025557612"],
        "email": ["info@ralphtester.me"],
        "topics": ["role.spy"],
    },
}


def make_proxy(schema, **data):
    proxy = model.make_entity(schema)
    for k, v in data.items():
        proxy.add(k, v)
    proxy.make_id(*random.sample(string.ascii_letters, 24))
    return proxy


class MultiPartProxyTestCase(TestCase):
    def test_base_functions(self):
        a = model.get_proxy(ENTITY)
        b = model.get_proxy(ENTITY)
        mpp = MultiPartProxy(proxies=[a, b])
        assert len(mpp.proxies) == 1
        assert len(mpp.get("name")) == 1
        assert mpp.get("name")[0] == "Ralph Tester"
        mpp_keys = mpp.properties.keys()
        assert set(a.properties.keys()) == mpp_keys
        mpp_inv_keys = mpp.get_type_inverted().keys()
        assert set(a.get_type_inverted().keys()) == mpp_inv_keys

    def test_schema(self):
        mpp = MultiPartProxy()
        proxy = make_proxy("Organization")
        mpp.add_proxy(proxy)
        assert mpp.schema.name == "Organization"

        proxy = make_proxy("PublicBody")
        mpp.add_proxy(proxy)
        assert mpp.schema.name == "PublicBody"

        proxy = make_proxy("Organization")
        mpp.add_proxy(proxy)
        assert mpp.schema.name == "PublicBody"

    def test_get(self):
        mpp = MultiPartProxy()
        proxies = set()
        for i in range(10):
            name = "".join(random.sample(string.ascii_letters, 8))
            proxy = make_proxy("Person", name=name)
            mpp.add_proxy(proxy)
            proxies.add(proxy)
        assert len(mpp.proxies) == 10
        assert len(mpp.get("name")) == 10
        assert all(p in mpp for p in proxies)

    def test_remove(self):
        mpp = MultiPartProxy()
        proxies = set()
        for i in range(10):
            name = "".join(random.sample(string.ascii_letters, 8))
            proxy = make_proxy("Person", name=name)
            mpp.add_proxy(proxy)
            proxies.add(proxy)
        remove = proxies.pop()
        mpp.discard(remove)
        assert len(mpp.proxies) == 9
        assert len(mpp.get("name")) == 9
        assert all(p in mpp for p in proxies)
        assert remove not in mpp

    def test_merge(self):
        proxies = []
        for i in range(3):
            proxy = make_proxy("Person")
            proxies.append(proxy)
        mpp1 = MultiPartProxy(proxies=[proxies[0]], anti_proxies=[proxies[1]])
        mpp2 = MultiPartProxy(proxies=[proxies[2]], anti_proxies=[proxies[0]])
        mpp1.merge(mpp2)

        assert len(mpp1.proxies) == 2
        assert len(mpp1.anti_proxies) == 1
        assert proxies[0] in mpp1
        assert proxies[1] in mpp1.anti_proxies
        assert proxies[2] in mpp1

        mpp1 = MultiPartProxy(proxies=[proxies[0]], anti_proxies=[proxies[1]])
        mpp2 = MultiPartProxy(proxies=[proxies[1]], anti_proxies=[proxies[0]])
        mpp1.merge(mpp2)

        assert len(mpp1.proxies) == 1
        assert len(mpp1.anti_proxies) == 1
        assert proxies[0] in mpp1
        assert proxies[1] in mpp1.anti_proxies

from followthemoney.exc import InvalidData
from followthemoney.proxy import EntityProxy


class MultiPartProxy(EntityProxy):
    def __init__(self, id=None, proxies=None, anti_proxies=None):
        self.id = id
        self.proxies = set(proxies or [])
        self.anti_proxies = set(anti_proxies or [])
        self._golden_proxy = None
        self._build()

    def _build(self):
        if not self.proxies:
            return
        _golden_proxy = None
        for proxy in self.proxies:
            if _golden_proxy is None:
                _golden_proxy = proxy.clone()
            _golden_proxy.merge(proxy)
        self._golden_proxy = _golden_proxy

    def _merge_new_proxy(self, proxy):
        if self._golden_proxy is None:
            self._build()
            return
        self._golden_proxy.merge(proxy)

    @property
    def golden_proxy(self):
        if self._golden_proxy is not None:
            return self._golden_proxy.clone()
        return None

    @property
    def schema(self):
        if self._golden_proxy is None:
            return None
        return self._golden_proxy.schema

    @property
    def _properties(self):
        if self._golden_proxy is None:
            return {}
        return self._golden_proxy._properties

    @property
    def parts(self):
        return [p.id for p in self.proxies]

    @property
    def anti_parts(self):
        return [p.id for p in self.anti_proxies]

    def add(self, prop, values):
        raise NotImplementedError

    def merge(self, other):
        self.id = self.id or other.id
        self.proxies.update(other.proxies - self.anti_proxies)
        self.anti_proxies.update(other.anti_proxies - self.proxies)
        self._build()
        return self

    def add_proxy(self, proxy):
        if proxy not in self.proxies:
            self.proxies.add(proxy)
            try:
                self._merge_new_proxy(proxy)
            except InvalidData:
                self.proxies.discard(proxy)
                raise
        self.anti_proxies.discard(proxy)

    def add_anti_proxy(self, proxy):
        self.anti_proxies.add(proxy)
        if proxy in self.proxies:
            self.proxies.discard(proxy)
            self._build()

    def discard(self, proxy):
        self.anti_proxies.discard(proxy)
        if proxy in self.proxies:
            self.proxies.discard(proxy)
            self._build()

    def __contains__(self, proxy):
        return proxy in self.proxies

    def to_dict(self):
        return {
            "id": self.id,
            "schema": self.schema.name,
            "parts": self.parts,
            "anti_parts": self.anti_parts,
            "proxies": self.proxies,
            "anti_proxies": self.anti_proxies,
        }

    def __repr__(self):
        return "<MPP(%r,%r)>" % (self.id, str(self))

import hmac

from followthemoney.types import registry
from followthemoney.util import key_bytes, get_entity_id


class Namespace(object):
    """Namespaces are used to partition entity IDs into different units,
    which traditionally represent a dataset, collection or source."""
    # cf. https://github.com/alephdata/followthemoney/issues/35
    SEP = '.'

    def __init__(self, name=None):
        self.bname = key_bytes(name) if name else b''
        self.hmac = hmac.new(self.bname, digestmod='sha1')

    @classmethod
    def parse(cls, entity_id):
        """Split up an entity ID into the plain ID and the namespace
        signature. If either part is missing, return None instead."""
        entity_id = registry.entity.clean(entity_id)
        if entity_id is None:
            return (None, None)
        try:
            plain_id, checksum = entity_id.rsplit(cls.SEP, 1)
            return (plain_id, checksum)
        except ValueError:
            return (entity_id, None)

    @classmethod
    def strip(cls, entity_id):
        plain_id, _ = cls.parse(entity_id)
        return plain_id

    def signature(self, entity_id):
        """Generate a namespace-specific signature."""
        if not len(self.bname) or entity_id is None:
            return None
        digest = self.hmac.copy()
        digest.update(key_bytes(entity_id))
        return digest.hexdigest()

    def sign(self, entity_id):
        """Apply a namespace signature to an entity ID, removing any
        previous namespace marker."""
        entity_id, _ = self.parse(entity_id)
        if not len(self.bname):
            return entity_id
        if entity_id is None:
            return None
        digest = self.signature(entity_id)
        return self.SEP.join((entity_id, digest))

    def verify(self, entity_id):
        """Check if the signature matches the current namespace."""
        entity_id, digest = self.parse(entity_id)
        if digest is None:
            return False
        return hmac.compare_digest(digest, self.signature(entity_id))

    def apply(self, proxy):
        """Rewrite an entity proxy so all IDs mentioned are limited to
        the namespace.

        An exception is made for sameAs declarations."""
        signed = proxy.clone()
        signed.id = self.sign(proxy.id)
        for prop in proxy.iterprops():
            if prop.type != registry.entity:
                continue
            for value in signed.pop(prop):
                value = get_entity_id(value)
                signed.add(prop, self.sign(value))
        # linked.add('sameAs', proxy.id, quiet=True)
        signed.remove('sameAs', signed.id)
        return signed

    @classmethod
    def make(cls, name):
        if isinstance(name, cls):
            return name
        return cls(name)

    def __eq__(self, other):
        return self.bname == other.bname

    def __repr__(self):
        return '<Namespace(%r)>' % self.bname

"""
*We like our abstractions like our offshore banks: leaky.*

Entity ID namespaces are a security mechanism related to the Aleph search index.
When bulk-loading entities associated with a particular dataset to the index,
past versions of Aleph would first look up each entity ID in the index, check
that it was part of the same dataset as the new entity, and only then proceed
to write the index.

The root cause for this issue is because Aleph allows the user (via mappings
or the API) to specify entity IDs. The fact that entity IDs are controlled by
the user and not the system is, of course, unusual. At the same time, it makes
it possible to generate bulk data outside Aleph, and then load it into the
system as a continuous stream of entities.

Namespacing works around this by essentially making a compromise: the entity ID
consists of two parts: one controlled by the client, the other controlled by
the system. The logic is basically `{entity_id}.{signature}`, where `signature`
is `hmac(entity_id, dataset_id)`. This, first of all, guarantees that the
combined ID is specific to a dataset, without needing an (expensive) index
look up of each ID first. It can also be generated both on the client and in
the server without compromising isolation.
"""
import hmac

from followthemoney.types import registry
from followthemoney.util import key_bytes, get_entity_id


class Namespace(object):
    """Namespaces are used to partition entity IDs into different units,
    which traditionally represent a dataset, collection or source.

    See module docstring for details."""

    SEP = "."

    def __init__(self, name=None):
        self.bname = key_bytes(name) if name else b""
        self.hmac = hmac.new(self.bname, digestmod="sha1")

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

    def apply(self, proxy, shallow=False):
        """Rewrite an entity proxy so all IDs mentioned are limited to
        the namespace."""
        signed = proxy.clone()
        signed.id = self.sign(proxy.id)
        if not shallow:
            for prop in proxy.iterprops():
                if prop.type != registry.entity:
                    continue
                for value in signed.pop(prop):
                    value = get_entity_id(value)
                    signed.add(prop, self.sign(value))
        return signed

    @classmethod
    def make(cls, name):
        if isinstance(name, cls):
            return name
        return cls(name)

    def __eq__(self, other):
        return self.bname == other.bname

    def __repr__(self):
        return "<Namespace(%r)>" % self.bname

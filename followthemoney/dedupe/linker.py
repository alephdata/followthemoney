from followthemoney.types import registry
from followthemoney.namespace import Namespace
from followthemoney.dedupe import Match


class Linker(object):
    """Utility class to resolve entity IDs which have been marked
    identical in a recon file."""

    def __init__(self, model, namespace=None):
        self.model = model
        self.ns = namespace or Namespace()
        self.lookup = {}

    def add(self, match):
        if match.decision == Match.SAME:
            entity_id = self.ns.sign(match.entity_id)
            self.lookup[entity_id] = self.ns.sign(match.id)

    def resolve(self, entity_id):
        """Given an entity or entity ID, return the canonicalised ID that
        should be used going forward."""
        canonical_id = self.lookup.get(entity_id, entity_id)
        if canonical_id != entity_id:
            # Recurse for good luck.
            canonical_id = self.resolve(canonical_id)
        return canonical_id

    def apply(self, proxy):
        """Rewrite an entity proxy so that both its own ID and any references
        to other entities in the properties are canonicalised."""
        # NOTE: Applying linkage merges namespaces. This is the simplest way
        # to deal with this issue - and it abstractly matches the concept of
        # data intgration.
        linked = self.ns.apply(proxy)
        linked.id = self.resolve(linked.id)
        linked.context = {}
        for prop in proxy.iterprops():
            if prop.type != registry.entity:
                continue
            for value in linked.pop(prop):
                if prop.name != 'sameAs':
                    value = self.resolve(value)
                linked.add(prop, value)
        # linked.remove('sameAs', linked.id)
        return linked

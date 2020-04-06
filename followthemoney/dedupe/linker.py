from followthemoney.util import get_entity_id
from followthemoney.types import registry
from followthemoney.namespace import Namespace
from followthemoney.dedupe import Match


class Linker(object):
    """Utility class to resolve entity IDs which have been marked
    identical in a recon file."""

    def __init__(self):
        self.lookup = {}

    def add(self, match):
        if match.decision == Match.SAME:
            self.lookup[match.naive_id] = match.canonical_id

    def resolve(self, entity_id):
        """Given an entity or entity ID, return the canonicalised ID that
        should be used going forward."""
        entity_id = Namespace.strip(get_entity_id(entity_id))
        canonical_id = self.lookup.get(entity_id, entity_id)
        if canonical_id != entity_id:
            # Recurse for good luck.
            canonical_id = self.resolve(canonical_id)
        return canonical_id

    def apply(self, proxy):
        """Rewrite an entity proxy so that both its own ID and any references
        to other entities in the properties are canonicalised."""
        linked = proxy.clone()
        linked.id = self.resolve(proxy.id)
        for prop in proxy.iterprops():
            if prop.type != registry.entity:
                continue
            for value in linked.pop(prop):
                if prop.name != 'sameAs':
                    value = self.resolve(value)
                linked.add(prop, value)
        # linked.remove('sameAs', linked.id)
        return linked

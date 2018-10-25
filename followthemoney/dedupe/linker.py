from followthemoney.types import registry
from followthemoney.util import get_entity_id


class EntityLinker(object):
    """Utility class to resolve entity IDs which have been marked
    identical in a recon file."""

    def __init__(self):
        self.linkages = {}

    def add(self, subject, canonical):
        subject = get_entity_id(subject)
        canonical = get_entity_id(canonical)

        # Don't do no-ops.
        if subject == canonical:
            return
        if subject is None or canonical is None:
            return
        resolved = self.resolve(canonical)

        # Circular dependencies
        if resolved == subject:
            resolved = max(subject, canonical)
            subject = min(subject, canonical)

        # Find existing references
        subjects = [subject]
        for (src, dst) in self.linkages.items():
            if dst == subject:
                subjects.append(src)
        for sub in subjects:
            if sub != resolved:
                self.linkages[sub] = resolved

    def has(self, subject):
        subject = get_entity_id(subject)
        return subject in self.linkages

    def resolve(self, subject):
        """Given an entity or entity ID, return the canonicalised ID that
        should be used going forward."""
        subject = get_entity_id(subject)
        return self.linkages.get(subject, subject)

    def apply(self, proxy):
        """Rewrite an entity proxy so that both its own ID and any references
        to other entities in the properties are canonicalised."""
        linked = proxy.clone()
        linked.id = self.resolve(proxy.id)
        for prop in proxy.iterprops():
            if prop.type != registry.entity:
                continue
            for value in linked.pop(prop):
                value = self.resolve(value)
                linked.add(prop, value)
        return linked

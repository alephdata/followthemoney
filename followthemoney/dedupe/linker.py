from hashlib import sha1

from followthemoney.types import registry
from followthemoney.util import get_entity_id


class Cluster(object):

    def __init__(self, *entities):
        self._id = None
        self.entities = set(entities)

    def update(self, entities):
        self._id = None
        self.entities.update(entities)

    @property
    def id(self):
        if self._id is None:
            key = ''.join(sorted(self.entities))
            if isinstance(key, str):
                key = key.encode('utf-8')
            self._id = sha1(key).hexdigest()
        return self._id


class EntityLinker(object):
    """Utility class to resolve entity IDs which have been marked
    identical in a recon file."""

    def __init__(self):
        self.clusters = {}

    def add(self, subject, canonical):
        subject = get_entity_id(subject)
        canonical = get_entity_id(canonical)

        # Don't do no-ops.
        if subject == canonical:
            return
        if subject is None or canonical is None:
            return

        cluster = Cluster(canonical, subject)
        cluster = self.clusters.get(canonical, cluster)
        if subject in self.clusters:
            previous = self.clusters.get(subject)
            cluster.update(previous.entities)

        for entity in cluster.entities:
            self.clusters[entity] = cluster

    def has(self, subject):
        subject = get_entity_id(subject)
        return subject in self.clusters

    def resolve(self, subject):
        """Given an entity or entity ID, return the canonicalised ID that
        should be used going forward."""
        subject = get_entity_id(subject)
        cluster = self.clusters.get(subject)
        if cluster is None:
            return subject
        return cluster.id

    def apply(self, proxy):
        """Rewrite an entity proxy so that both its own ID and any references
        to other entities in the properties are canonicalised."""
        linked = proxy.clone()
        cluster = self.clusters.get(proxy.id)
        if cluster is not None:
            linked.id = cluster.id
            linked.add('sameAs', cluster.entities, quiet=True)
        for prop in proxy.iterprops():
            if prop.type != registry.entity:
                continue
            for value in linked.pop(prop):
                if prop.name == 'sameAs':
                    linked.add(prop, value)
                else:
                    linked.add(prop, self.resolve(value))
        return linked

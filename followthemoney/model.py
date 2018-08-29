import os
import yaml

from followthemoney.schema import Schema
from followthemoney.link import Link
from followthemoney.mapping import QueryMapping
from followthemoney.util import merge_data
from followthemoney.exc import InvalidModel, InvalidData


class Model(object):
    """A collection of schemata."""

    def __init__(self, path):
        self.path = path
        self.schemata = {}
        for (path, _, filenames) in os.walk(self.path):
            for filename in filenames:
                self._load(os.path.join(path, filename))
        self.generate()

    def generate(self):
        self.properties = set()
        for schema in self:
            schema.generate()
            for prop in schema.properties.values():
                self.properties.add(prop)

    def _load(self, filepath):
        with open(filepath, 'r') as fh:
            data = yaml.load(fh)
            if not isinstance(data, dict):
                raise InvalidModel('Model file is not a mapping.')
            for name, config in data.items():
                self.schemata[name] = Schema(self, name, config)

    def get(self, name):
        if isinstance(name, Schema):
            return name
        return self.schemata.get(name)

    def get_qname(self, qname):
        if not hasattr(self, '_qnames'):
            self._qnames = {p.qname: p for p in self.properties}
        return self._qnames.get(qname)

    def __getitem__(self, name):
        schema = self.get(name)
        if schema is None:
            raise KeyError("No such schema: %s" % name)
        return schema

    def make_mapping(self, mapping, key_prefix=None):
        """Parse a mapping that applies (tabular) source data to the model."""
        return QueryMapping(self, mapping, key_prefix=key_prefix)

    def map_entities(self, mapping, key_prefix=None):
        """Given a mapping, yield a series of entities from the data source."""
        mapping = self.make_mapping(mapping, key_prefix=key_prefix)
        for record in mapping.source.records:
            for entity in mapping.map(record).values():
                yield entity

    def precise_schema(self, left, right):
        """Select the most narrow of two schemata.

        When indexing data from a dataset, an entity may be declared as a
        LegalEntity in one query, and as a Person in another. This function
        will select the most specific of two schemata offered. In the example,
        that would be Person.
        """
        if left == right:
            return left
        lefts = self.get(left)
        if lefts is None:
            return right
        if right in lefts.names:
            return left

        rights = self.get(right)
        if rights is None:
            return left
        if left in rights.names:
            return right

        # Find a common ancestor:
        for left in lefts.names:
            for right in rights.names:
                if left == right:
                    return left

        raise InvalidData("No common ancestor: %s and %s" % (left, right))

    def merge(self, left, right):
        """Merge two entities and return a combined version."""
        properties = merge_data(left.get('properties'),
                                right.get('properties'))
        schema = self.precise_schema(left.get('schema'),
                                     right.get('schema'))
        return {
            'id': left.get('id', right.get('id')),
            'schema': schema,
            'properties': properties
        }

    def entity_links(self, entity):
        yield from Link.from_entity(self, entity)

    def entity_rdf(self, entity):
        for link in self.entity_links(entity):
            triple = link.rdf()
            if triple is not None:
                yield triple

    def to_dict(self):
        return {n: s.to_dict() for (n, s) in self.schemata.items()}

    def __iter__(self):
        return iter(self.schemata.values())

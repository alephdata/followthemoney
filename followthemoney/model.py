import os
import yaml

from followthemoney.schema import Schema
from followthemoney.mapping import QueryMapping, get_source
from followthemoney.util import merge_data
from followthemoney.exc import InvalidModel


class Model(object):
    """A collection of schemata."""

    def __init__(self, path):
        self.path = path

    @property
    def schemata(self):
        if not hasattr(self, '_schemata'):
            self._schemata = {}
            for (path, _, filenames) in os.walk(self.path):
                for filename in filenames:
                    self._load(os.path.join(path, filename))
        return self._schemata

    @property
    def properties(self):
        props = set()
        for schema in self.schemata.values():
            for prop in schema.properties.values():
                props.add(prop)
        return props

    @property
    def property_types(self):
        prop_types = {}
        for prop in self.properties:
            prop_types[prop.name] = prop.type_name
        return prop_types

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

    def __getitem__(self, name):
        schema = self.get(name)
        if schema is None:
            raise KeyError("No such schema: %s" % name)
        return schema

    def make_mapping(self, mapping, key_prefix=None):
        """Parse a mapping that applies (tabular) source data to the model."""
        mapping = QueryMapping(self, mapping, key_prefix=key_prefix)
        mapping.source = get_source(mapping)
        return mapping

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

        raise InvalidModel("No common ancestor: %s and %s" % (left, right))

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

    def to_dict(self):
        return {n: s.to_dict() for (n, s) in self.schemata.items()}

    def __iter__(self):
        return iter(self.schemata.values())

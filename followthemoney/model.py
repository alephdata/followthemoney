import os
import yaml

from followthemoney.schema import Schema
from followthemoney.mapping import QueryMapping, get_source
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

    def make_mapping(self, mapping, key_prefix=None):
        """Parse a mapping that applies (tabular) source data to the model."""
        return QueryMapping(self, mapping, key_prefix=key_prefix)

    def map_entities(self, mapping, key_prefix=None):
        """Given a mapping, yield a series of entities from the data source."""
        mapping = self.make_mapping(mapping, key_prefix=key_prefix)
        for record in get_source(mapping).records:
            for entity in mapping.map(record).values():
                yield entity

    def merge_entity_schema(self, left, right):
        """Select the most narrow of two schemata.

        When indexing data from a dataset, an entity may be declared as a
        LegalEntity in one query, and as a Person in another. This function
        will select the most specific of two schemata offered. In the example,
        that would be Person.
        """
        if left == right:
            return left
        lefts = self.get(left)
        lefts = [s.name for s in lefts.schemata]
        if right in lefts:
            return left

        rights = self.get(right)
        rights = [s.name for s in rights.schemata]
        if left in rights:
            return right

        for left in lefts:
            for right in rights:
                if left == right:
                    return left

    def to_dict(self):
        data = {}
        for name, schema in self.schemata.items():
            if not schema.hidden:
                data[name] = schema.to_dict()
        return data

    def __iter__(self):
        return iter(self.schemata.values())

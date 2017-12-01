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
        lefts = [s.name for s in lefts.schemata]
        if right in lefts:
            return left

        rights = self.get(right)
        if rights is None:
            return left
        rights = [s.name for s in rights.schemata]
        if left in rights:
            return right

        for left in lefts:
            for right in rights:
                if left == right:
                    return left

        raise InvalidModel("No common ancestor: %s and %s" % (left, right))

    def is_descendant(self, parent, child):
        """ Find out if a child schema extends parent."""
        if parent == child:
            return True
        childs = self.get(child)
        ancestors = childs.schemata
        if parent in [s.name for s in ancestors]:
            return True
        return False

    def merge(self, left, right):
        """Merge two entities and return a combined version."""
        properties = merge_data(left.get('properties'),
                                right.get('properties'))
        return {
            'schema': self.precise_schema(left.get('schema'),
                                          right.get('schema')),
            'id': left.get('id', right.get('id')),
            'properties': properties,
            'data': merge_data(left.get('data'), right.get('data'))
        }

    def to_dict(self):
        data = {}
        for name, schema in self.schemata.items():
            if not schema.hidden:
                data[name] = schema.to_dict()
        return data

    def __iter__(self):
        return iter(self.schemata.values())

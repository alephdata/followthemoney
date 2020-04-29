import os
import yaml
from typing import Dict, Union, Set, Optional, Any, Mapping

from followthemoney.types import registry
from followthemoney.schema import Schema
from followthemoney.property import Property
from followthemoney.mapping import QueryMapping
from followthemoney.proxy import EntityProxy
from followthemoney.exc import InvalidModel, InvalidData


class Model(object):
    """A collection of schemata."""

    def __init__(self, path: str):
        self.path: str = path
        self.schemata: Dict[str, Schema] = {}
        self.properties: Dict[str, Property] = {}
        self.qnames: Dict[str, str] = {}
        for (path, _, filenames) in os.walk(self.path):
            for filename in filenames:
                self._load(os.path.join(path, filename))
        self.generate()

    def generate(self):
        for schema in self:
            schema.generate()
        for prop in self.properties:
            self.qnames[prop.qname] = prop
            # FIXME: stubs are not correctly assigned
            for schema in prop.schema.descendants:
                if prop.name not in schema.properties:
                    schema.properties[prop.name] = prop

    def _load(self, filepath: str):
        with open(filepath, 'r') as fh:
            data = yaml.safe_load(fh)
            if not isinstance(data, dict):
                raise InvalidModel('Model file is not a mapping.')
            for name, config in data.items():
                self.schemata[name] = Schema(self, name, config)

    def get(self, name: Union[str, Schema]) -> Optional[Schema]:
        if isinstance(name, Schema):
            return name
        return self.schemata.get(name)

    def get_qname(self, qname: str) -> Optional[str]:
        return self.qnames.get(qname)

    def __getitem__(self, name: str) -> Schema:
        schema = self.get(name)
        if schema is None:
            raise KeyError("No such schema: %s" % name)
        return schema

    def get_type_schemata(self, type_: str) -> Set[Schema]:
        """Return all the schemata which have a property of the given type."""
        schemata = set()
        for schema in self.schemata.values():
            for prop in schema.properties.values():
                if prop.type == type_:
                    schemata.add(schema)
        return schemata

    def make_mapping(self, mapping: Dict[str, Any], key_prefix=None):
        """Parse a mapping that applies (tabular) source data to the model."""
        return QueryMapping(self, mapping, key_prefix=key_prefix)

    def map_entities(self, mapping: Dict[str, Any], key_prefix=None):
        """Given a mapping, yield a series of entities from the data source."""
        q_mapping = self.make_mapping(mapping, key_prefix=key_prefix)
        for record in q_mapping.source.records:
            for entity in q_mapping.map(record).values():
                yield entity

    def common_schema(self, left: Union[str, Schema], right: Union[str, Schema]) -> Schema:
        """Select the most narrow of two schemata.

        When indexing data from a dataset, an entity may be declared as a
        LegalEntity in one query, and as a Person in another. This function
        will select the most specific of two schemata offered. In the example,
        that would be Person.
        """
        left_schema = self.get(left) or self.get(right)
        if left_schema is None:
            # neither left nor right are valid schemata
            msg = "Unknown schemata: %s and %s"
            raise InvalidData(msg % (left, right))

        right_schema = self.get(right) or self.get(left)
        if right_schema is None:
            # neither left nor right are valid schemata
            msg = "Unknown schemata: %s and %s"
            raise InvalidData(msg % (left, right))

        if left_schema.is_a(right_schema):
            return left_schema
        if right_schema.is_a(left_schema):
            return right_schema
        common = list(left_schema.schemata.intersection(right_schema.schemata))
        if not len(common):
            msg = "No common ancestor: %s and %s"
            raise InvalidData(msg % (left_schema, right_schema))

        specific = common[0]
        for schema in common[1:]:
            if schema.is_a(specific):
                specific = schema
        return specific

    def make_entity(self, schema: Mapping, key_prefix=None) -> EntityProxy:
        return EntityProxy(self, {'schema': schema}, key_prefix=key_prefix)

    def get_proxy(self, data: Mapping, cleaned=True) -> EntityProxy:
        return EntityProxy.from_dict(self, data, cleaned=cleaned)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'schemata': {s.name: s.to_dict() for s in self.schemata.values()},
            'types': {t.name: t.to_dict() for t in registry.types}
        }

    def __iter__(self):
        return iter(self.schemata.values())

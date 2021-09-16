from hashlib import sha1
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set
from banal import keys_values
from normality import stringify

from followthemoney.types import registry
from followthemoney.util import key_bytes
from followthemoney.proxy import EntityProxy
from followthemoney.mapping.property import PropertyMapping
from followthemoney.mapping.source import Record
from followthemoney.exc import InvalidData, InvalidMapping

if TYPE_CHECKING:
    from followthemoney.model import Model
    from followthemoney.mapping.query import QueryMapping


class EntityMapping(object):

    __slots__ = (
        "model",
        "name",
        "seed",
        "keys",
        "id_column",
        "schema",
        "refs",
        "dependencies",
        "properties",
    )

    def __init__(
        self,
        model: "Model",
        query: "QueryMapping",
        name: str,
        data: Dict[str, Any],
        key_prefix: Optional[str] = None,
    ) -> None:
        self.model = model
        self.name = name

        self.seed = sha1(key_bytes(key_prefix))
        self.seed.update(key_bytes(data.get("key_literal")))

        self.keys = keys_values(data, "key", "keys")
        self.id_column = stringify(data.get("id_column"))
        if not len(self.keys) and self.id_column is None:
            raise InvalidMapping("No keys or ID: %r" % name)
        if len(self.keys) and self.id_column is not None:
            msg = "Please use only keys or id_column, not both: %r" % name
            raise InvalidMapping(msg)

        schema_name = stringify(data.get("schema"))
        if schema_name is None:
            raise InvalidMapping("No schema: %s" % name)
        schema = model.get(schema_name)
        if schema is None:
            raise InvalidMapping("Invalid schema: %s" % schema_name)
        self.schema = schema

        self.refs = set(self.keys)
        if self.id_column:
            self.refs.add(self.id_column)
        self.dependencies: Set[str] = set()
        self.properties: List[PropertyMapping] = []
        for name, prop_mapping in data.get("properties", {}).items():
            prop = self.schema.get(name)
            if prop is None:
                raise InvalidMapping("Invalid property: %s" % name)
            mapping = PropertyMapping(query, prop_mapping, prop)
            self.properties.append(mapping)
            self.refs.update(mapping.refs)
            if mapping.entity:
                self.dependencies.add(mapping.entity)

    def bind(self) -> None:
        for prop in self.properties:
            prop.bind()

    def compute_key(self, record: Record) -> Optional[str]:
        """Generate a key for this entity, based on the given fields."""
        if self.id_column is not None:
            return record.get(self.id_column)
        values = [key_bytes(record.get(k)) for k in self.keys]
        digest = self.seed.copy()
        has_value = False
        for value in sorted(values):
            if len(value):
                has_value = True
                digest.update(value)
        if has_value:
            return digest.hexdigest()
        return None

    def map(
        self, record: Record, entities: Dict[str, EntityProxy]
    ) -> Optional[EntityProxy]:
        proxy = self.model.make_entity(self.schema)

        # THIS IS HACKY
        # Some of the converters, e.g. for phone numbers, work better if they
        # know the country which the number is from. In order to provide that
        # detail, we are first running country fields, then making the data
        # from that accessible to phone and address parsers.
        for prop in self.properties:
            if prop.prop.type == registry.country:
                prop.map(proxy, record, entities)

        for prop in self.properties:
            if prop.prop.type != registry.country:
                prop.map(proxy, record, entities)

        # Generate the ID at the end to avoid self-reference checks on empty
        # keys.
        proxy.id = self.compute_key(record)
        if proxy.id is None:
            return None

        for prop in self.properties:
            if prop.required and not proxy.has(prop.prop):
                # This is a bit weird, it flags fields to be required in
                # the mapping, not in the model. Basically it means: if
                # this row of source data doesn't have that field, then do
                # not map it again.
                return None
        return proxy

    def __repr__(self) -> str:
        return "<EntityMapping(%r)>" % self.name

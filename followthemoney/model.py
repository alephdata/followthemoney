import os
import yaml
from typing import Any, Dict, Generator, Iterator, Optional, Set, TypedDict, Union

from followthemoney.types import registry
from followthemoney.types.common import PropertyType, PropertyTypeToDict
from followthemoney.schema import Schema, SchemaToDict
from followthemoney.property import Property
from followthemoney.mapping import QueryMapping
from followthemoney.proxy import EntityProxy
from followthemoney.exc import InvalidModel, InvalidData


class ModelToDict(TypedDict):
    schemata: Dict[str, SchemaToDict]
    types: Dict[str, PropertyTypeToDict]


class Model(object):
    """A collection of all the schemata available in followthemoney. The model
    provides some helper functions to find schemata, properties or to instantiate
    entity proxies based on the schema metadata."""

    __slots__ = ("path", "schemata", "properties", "qnames")

    def __init__(self, path: str) -> None:
        self.path = path

        #: A mapping with all schemata, organised by their name.
        self.schemata: Dict[str, Schema] = {}

        #: All properties defined in the model.
        self.properties: Set[Property] = set()
        self.qnames: Dict[str, Property] = {}
        for (path, _, filenames) in os.walk(self.path):
            for filename in filenames:
                self._load(os.path.join(path, filename))
        self.generate()

    def generate(self) -> None:
        """Loading the model is a weird process because the schemata reference
        each other in complex ways, so the generation process cannot be fully
        run as schemata are being instantiated. Hence this process needs to be
        called once all schemata are loaded to finalise dereferencing the
        schemata."""
        for schema in self:
            schema.generate()
        for prop in self.properties:
            self.qnames[prop.qname] = prop
            # FIXME: stubs are not correctly assigned
            for schema in prop.schema.descendants:
                if prop.name not in schema.properties:
                    schema.properties[prop.name] = prop

    def _load(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            if not isinstance(data, dict):
                raise InvalidModel("Model file is not a mapping: %s" % filepath)
            for name, config in data.items():
                self.schemata[name] = Schema(self, name, config)

    def get(self, name: Union[str, Schema]) -> Optional[Schema]:
        """Get a schema object based on a schema name. If the input is already
        a schema object, it will just be returned."""
        if isinstance(name, str):
            return self.schemata.get(name)
        return name

    def get_qname(self, qname: str) -> Optional[Property]:
        """Get a property object based on a qualified name (i.e. schema:property)."""
        return self.qnames.get(qname)

    def __getitem__(self, name: str) -> Schema:
        """Same as get(), but throws an exception when the given name does not exist."""
        schema = self.get(name)
        if schema is None:
            raise KeyError("No such schema: %s" % name)
        return schema

    def get_type_schemata(self, type_: PropertyType) -> Set[Schema]:
        """Return all the schemata which have a property of the given type."""
        schemata = set()
        for schema in self.schemata.values():
            for prop in schema.properties.values():
                if prop.type == type_:
                    schemata.add(schema)
        return schemata

    def make_mapping(
        self, mapping: Dict[str, Any], key_prefix: Optional[str] = None
    ) -> QueryMapping:
        """Parse a mapping that applies (tabular) source data to the model."""
        return QueryMapping(self, mapping, key_prefix=key_prefix)

    def map_entities(
        self, mapping: Dict[str, Any], key_prefix: Optional[str] = None
    ) -> Generator[EntityProxy, None, None]:
        """Given a mapping, yield a series of entities from the data source."""
        gen = self.make_mapping(mapping, key_prefix=key_prefix)
        for record in gen.source.records:
            for entity in gen.map(record).values():
                yield entity

    def common_schema(
        self, left: Union[str, Schema], right: Union[str, Schema]
    ) -> Schema:
        """Select the most narrow of two schemata.

        When indexing data from a dataset, an entity may be declared as a
        LegalEntity in one query, and as a Person in another. This function
        will select the most specific of two schemata offered. In the example,
        that would be Person.
        """
        left_schema = self.get(left) or self.get(right)
        right_schema = self.get(right) or self.get(left)
        if left_schema is None or right_schema is None:
            raise InvalidData("Invalid schema")
        if left_schema.is_a(right_schema):
            return left_schema
        if right_schema.is_a(left_schema):
            return right_schema
        # for schema in self.schemata.values():
        #     if schema.is_a(left) and schema.is_a(right):
        #         return schema
        msg = "No common schema: %s and %s"
        raise InvalidData(msg % (left, right))

    def make_entity(
        self, schema: Union[str, Schema], key_prefix: Optional[str] = None
    ) -> EntityProxy:
        """Instantiate an empty entity proxy of the given schema type."""
        return EntityProxy(self, {"schema": schema}, key_prefix=key_prefix)

    def get_proxy(self, data: Dict[str, Any], cleaned: bool = True) -> EntityProxy:
        """Create an entity proxy to reflect the entity data in the given
        dictionary. If ``cleaned`` is disabled, all property values are
        fully re-validated and normalised. Use this if handling input data
        from an untrusted source."""
        if isinstance(data, EntityProxy):
            return data
        return EntityProxy.from_dict(self, data, cleaned=cleaned)

    def to_dict(self) -> ModelToDict:
        """Return metadata for all schemata and properties, in a serializable form."""
        return {
            "schemata": {s.name: s.to_dict() for s in self.schemata.values()},
            "types": {t.name: t.to_dict() for t in registry.types},
        }

    def __iter__(self) -> Iterator[Schema]:
        """Iterate across all schemata."""
        return iter(self.schemata.values())

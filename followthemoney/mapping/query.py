from followthemoney.mapping.source import Record, Source
from typing import TYPE_CHECKING, Any, List, Optional, Set, Dict

from followthemoney.proxy import EntityProxy
from followthemoney.mapping.entity import EntityMapping
from followthemoney.mapping.sql import SQLSource
from followthemoney.mapping.csv import CSVSource
from followthemoney.exc import InvalidMapping

if TYPE_CHECKING:
    from followthemoney.model import Model


class QueryMapping:
    __slots__ = ("model", "data", "refs", "entities")

    def __init__(
        self, model: "Model", data: Dict[str, Any], key_prefix: Optional[str] = None
    ) -> None:
        self.model = model
        self.data = data
        self.refs = set[str]()
        self.entities: List[EntityMapping] = []
        for name, data in data.get("entities", {}).items():
            entity = EntityMapping(model, self, name, data, key_prefix=key_prefix)

            self.entities.append(entity)
            self.refs.update(entity.refs)

        if not len(self.entities):
            raise InvalidMapping("No entity mappings are defined.")

        # Check if the provided links satisfy the ranges of the given
        # properties (e.g. the owner of a company must be a legal person)
        for entity in self.entities:
            entity.bind()

        # Do dependency resolution, i.e. find the right order to
        # map these entities. This is needed to resolve entity IDs
        # in dependent entities.
        entities = self.entities
        self.entities = []
        resolved: Set[str] = set()
        while len(entities) > 0:
            before = len(entities)
            for entity in entities:
                if entity.dependencies.issubset(resolved):
                    self.entities.append(entity)
                    entities.remove(entity)
                    resolved.add(entity.name)
                    break
            if before == len(entities):
                raise InvalidMapping("Circular entity dependency detected.")

    @property
    def source(self) -> Source:
        if "database" in self.data:
            return SQLSource(self, self.data)
        elif "csv_url" in self.data or "csv_urls" in self.data:
            return CSVSource(self, self.data)
        raise InvalidMapping("Cannot determine mapping type")

    def map(self, record: Record) -> Dict[str, EntityProxy]:
        data: Dict[str, EntityProxy] = {}
        for entity in self.entities:
            mapped = entity.map(record, data)
            if mapped is not None:
                data[entity.name] = mapped
        return data

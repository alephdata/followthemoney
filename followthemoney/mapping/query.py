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
    __slots__ = ("model", "data", "refs", "entities", "source")

    def __init__(
        self, model: "Model", data: Dict[str, Any], key_prefix: Optional[str] = None
    ) -> None:
        self.model = model
        self.refs: Set[str] = set()
        self.entities: List[EntityMapping] = []
        for name, edata in data.get("entities", {}).items():
            entity = EntityMapping(model, self, name, edata, key_prefix=key_prefix)

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

        self.source = self._get_source(data)

    def _get_source(self, data: Dict[str, Any]) -> Source:
        if "database" in data:
            return SQLSource(self, data)
        if "csv_url" in data or "csv_urls" in data:
            return CSVSource(self, data)
        raise InvalidMapping("Cannot determine mapping type: %r" % data)

    def map(self, record: Record) -> Dict[str, EntityProxy]:
        data: Dict[str, EntityProxy] = {}
        for entity in self.entities:
            mapped = entity.map(record, data)
            if mapped is not None:
                data[entity.name] = mapped
        return data

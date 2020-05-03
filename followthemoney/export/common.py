from followthemoney.types import registry
from followthemoney.schema import Schema
from followthemoney.property import Property
from followthemoney.proxy import EntityProxy

from typing import Iterator, Tuple, List, Any


class Exporter(object):

    def __init__(self, export_all: bool=False):
        self.export_all: bool = export_all

    def exportable_properties(self, schema: Schema) -> Iterator[Property]:
        for prop in schema.sorted_properties:
            if not self.export_all:
                if prop.hidden or prop.type == registry.entity:
                    continue
            yield prop

    def exportable_fields(self, proxy: EntityProxy) -> Iterator[Tuple[Property, List[Any]]]:
        for prop in self.exportable_properties(proxy.schema):
            yield prop, proxy.get(prop)

    def write(self, proxy: EntityProxy, **kwargs):
        pass

    def finalize(self):
        pass

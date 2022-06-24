from typing import Dict, Iterable, List, Optional, TextIO, Union
import networkx as nx  # type: ignore
from networkx.readwrite.gexf import generate_gexf  # type: ignore

from followthemoney.graph import Edge, Graph, Node
from followthemoney.proxy import E
from followthemoney.types import registry
from followthemoney.export.common import Exporter

DEFAULT_EDGE_TYPES = (registry.entity.name,)


def edge_types() -> List[str]:
    return [t.name for t in registry.matchable if t is not None]


class GraphExporter(Exporter):
    """Base functions for exporting a property graph from a stream
    of entities."""

    def __init__(self, edge_types: Iterable[str] = DEFAULT_EDGE_TYPES) -> None:
        super(GraphExporter, self).__init__()
        types = registry.get_types(edge_types)
        self.graph = Graph(edge_types=types)

    def get_attributes(self, element: Union[Node, Edge]) -> Dict[str, str]:
        attributes = {}
        if element.proxy:
            for prop, values in self.exportable_fields(element.proxy):
                attributes[prop.name] = prop.type.join(values)
        return attributes

    def write(self, proxy: E, extra: Optional[List[str]] = None) -> None:
        self.graph.add(proxy)
        self.write_graph()

    def finalize(self) -> None:
        self.finalize_graph()
        self.graph.flush()

    def write_graph(self) -> None:
        pass

    def finalize_graph(self) -> None:
        pass


class NXGraphExporter(GraphExporter):
    """Write to NetworkX data structure, which in turn can be exported
    to the file formats for Gephi (GEXF) and D3."""

    def __init__(
        self, fh: TextIO, edge_types: Iterable[str] = DEFAULT_EDGE_TYPES
    ) -> None:
        super(NXGraphExporter, self).__init__(edge_types=edge_types)
        self.fh = fh

    def finalize_graph(self) -> None:
        """Convert from FtM graph model to NetworkX directed graph."""
        digraph = nx.MultiDiGraph()

        for node in self.graph.iternodes():
            attributes = self.get_attributes(node)
            attributes["schema"] = node.type.name
            if node.caption is not None:
                attributes["label"] = node.caption
            if node.is_entity and node.schema is not None:
                attributes["schema"] = node.schema.name
            digraph.add_node(node.id, **attributes)

        for edge in self.graph.iteredges():
            attributes = self.get_attributes(edge)
            attributes["schema"] = edge.type_name
            attributes["weight"] = str(edge.weight)
            digraph.add_edge(edge.source_id, edge.target_id, key=edge.id, **attributes)

        for line in generate_gexf(digraph, prettyprint=True):
            self.fh.write(line)
            self.fh.write("\n")

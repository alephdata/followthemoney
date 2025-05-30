import os
import json
import logging
from typing import Any, Dict, Iterable, List, Optional, Set, TextIO

from followthemoney.export.csv import CSVMixin, CSVWriter
from followthemoney.export.graph import GraphExporter, DEFAULT_EDGE_TYPES
from followthemoney.graph import Edge, Node
from followthemoney.schema import Schema
from followthemoney.util import PathLike, const_case

log = logging.getLogger(__name__)
NEO4J_ADMIN_PATH = os.environ.get("NEO4J_ADMIN_PATH", "neo4j-admin")
NEO4J_DATABASE_NAME = os.environ.get("NEO4J_DATABASE_NAME", "graph.db")


class Neo4JCSVExporter(CSVMixin, GraphExporter):
    def __init__(
        self,
        directory: PathLike,
        extra: Optional[List[str]] = None,
        edge_types: Iterable[str] = DEFAULT_EDGE_TYPES,
    ) -> None:
        super(Neo4JCSVExporter, self).__init__(edge_types=edge_types)
        self._configure(directory, extra=extra)

        self.links_handler, self.links_writer = self._open_csv_file("_links")
        self.links_writer.writerow([":TYPE", ":START_ID", ":END_ID", "weight"])

        self.nodes_handler, self.nodes_writer = self._open_csv_file("_nodes")
        self.nodes_writer.writerow(["id:ID", ":LABEL", "caption"])
        self.nodes_seen: Set[str] = set()

    def _write_header(self, writer: CSVWriter, schema: Schema) -> None:
        headers = []
        if not schema.edge:
            headers = ["id:ID", ":LABEL", "caption"]
        else:
            headers = ["id", ":TYPE", ":START_ID", ":END_ID"]

        headers.extend(self.extra)
        for prop in self.exportable_properties(schema):
            headers.append(prop.name)
        writer.writerow(headers)

    def write_graph(self, extra: Optional[List[str]] = None) -> None:
        extra_ = extra or []
        for node in self.graph.iternodes():
            self.write_node(node, extra_)

        for edge in self.graph.iteredges():
            self.write_edge(edge, extra_)

        self.graph.flush()

    def write_node(self, node: Node, extra: List[str]) -> None:
        if node.id is None:
            return None
        if not node.is_entity and node.id not in self.nodes_seen:
            row = [node.id, node.type.name, node.caption]
            self.nodes_writer.writerow(row)
            self.nodes_seen.add(node.id)
        if node.proxy is not None and node.schema is not None:
            label = ";".join(node.schema.names)
            cells = [node.id, label, node.caption]
            cells.extend(extra or [])
            for prop, values in self.exportable_fields(node.proxy):
                cells.append(prop.type.join(values))
            writer = self._get_writer(node.schema)
            writer.writerow(cells)

    def write_edge(self, edge: Edge, extra: List[str]) -> None:
        if edge.prop is not None:
            type_ = const_case(edge.prop.name)
            row = [type_, edge.source_id, edge.target_id, edge.weight]
            self.links_writer.writerow(row)
        if edge.proxy is not None:
            proxy = edge.proxy
            type_ = const_case(proxy.schema.name)
            # That potentially may lead to multiple edges with same id
            cells = [proxy.id, type_, edge.source_id, edge.target_id]
            cells.extend(extra or [])

            for prop, values in self.exportable_fields(edge.proxy):
                cells.append(prop.type.join(values))

            writer = self._get_writer(proxy.schema)
            writer.writerow(cells)

    def finalize_graph(self) -> None:
        script_path = self.directory.joinpath("neo4j_import.sh")
        with open(script_path, mode="w") as fp:
            cmd = "{} import --id-type=STRING --database={} \\\n"
            fp.write(cmd.format(NEO4J_ADMIN_PATH, NEO4J_DATABASE_NAME))
            fp.write("\t--multiline-fields=true \\\n")
            cmd = "\t--relationships={} \\\n"
            fp.write(cmd.format(os.path.basename(self.links_handler.name)))
            cmd = "\t--nodes={} \\\n"
            fp.write(cmd.format(os.path.basename(self.nodes_handler.name)))

            for schema, (handle, writer) in self.handles.items():
                file_name = os.path.basename(handle.name)
                if schema.edge:
                    cmd = "\t--relationships={} \\\n"
                    fp.write(cmd.format(file_name))
                else:
                    cmd = "\t--nodes={} \\\n"
                    fp.write(cmd.format(file_name))

        self.links_handler.close()
        self.nodes_handler.close()
        self.close()


class CypherGraphExporter(GraphExporter):
    """Cypher query format, used for import to Neo4J. This is a bit like
    writing SQL with individual statements - so for large datasets it
    might be a better idea to do a CSV-based import."""

    # https://www.opencypher.org/
    # MATCH (n) DETACH DELETE n;

    def __init__(self, fh: TextIO, edge_types: Iterable[str] = DEFAULT_EDGE_TYPES):
        super(CypherGraphExporter, self).__init__(edge_types=edge_types)
        self.fh = fh
        self.proxy_nodes: Set[str] = set()

    def _to_map(self, data: Dict[str, Any]) -> str:
        values = []
        for key, value in data.items():
            if value:
                value = "%s: %s" % (key, json.dumps(value))
                values.append(value)
        return ", ".join(values)

    def write_graph(self) -> None:
        """Export queries for each graph element."""
        for node in self.graph.iternodes():
            if node.value in self.proxy_nodes:
                continue
            if node.id is None:
                continue
            if node.proxy is not None:
                self.proxy_nodes.add(node.value)
            attributes = self.get_attributes(node)
            attributes["id"] = node.id
            if node.caption is not None:
                attributes["caption"] = node.caption
            if node.schema:
                labels = list(node.schema.names)
            else:
                labels = [node.type.name]
            cypher = "MERGE (p { %(id)s }) " "SET p += { %(map)s } SET p :%(label)s;\n"
            self.fh.write(
                cypher
                % {
                    "id": self._to_map({"id": node.id}),
                    "map": self._to_map(attributes),
                    "label": ":".join(labels),
                }
            )

        for edge in self.graph.iteredges():
            attributes = self.get_attributes(edge)
            attributes["id"] = edge.id
            attributes["weight"] = str(edge.weight)
            cypher = (
                "MATCH (s { %(source)s }), (t { %(target)s }) "
                "MERGE (s)-[:%(type)s { %(map)s }]->(t);\n"
            )
            self.fh.write(
                cypher
                % {
                    "source": self._to_map({"id": edge.source_id}),
                    "target": self._to_map({"id": edge.target_id}),
                    "type": const_case(edge.type_name),
                    "map": self._to_map(attributes),
                }
            )

        self.graph.flush()

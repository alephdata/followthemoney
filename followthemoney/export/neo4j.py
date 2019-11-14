import os
import csv
import json
import stringcase
from banal import ensure_list

from followthemoney.types import registry
from followthemoney.export.csv import CSVExporter
from followthemoney.export.graph import GraphExporter, DEFAULT_EDGE_TYPES

NEO4J_ADMIN_PATH = os.environ.get('NEO4J_ADMIN_PATH', 'bin/neo4j-admin')
NEO4J_DATABASE_NAME = os.environ.get('NEO4J_DATABASE_NAME', 'graph.db')


class Neo4JCSVExporter(CSVExporter, GraphExporter):
    def __init__(
        self,
        directory,
        dialect=csv.unix_dialect,
        extra=None,
        edge_types=DEFAULT_EDGE_TYPES,
    ):
        self.edge_types = edge_types
        extra = ['caption'] + ensure_list(extra)
        super().__init__(directory, dialect, extra)

        self.links_handler, self.links_writer = self._open_csv_file('_links')
        self.links_writer.writerow([':TYPE', ':START_ID', ':END_ID', 'weight'])

        self.nodes_handler, self.nodes_writer = self._open_csv_file('_nodes')
        self.nodes_writer.writerow(['id:ID', ':LABEL', 'caption'])
        self.nodes_seen = set()

    def _write_header(self, writer, schema):
        headers = []
        if not schema.edge:
            headers = ['id:ID', ':LABEL']
        else:
            headers = ['id', ':TYPE', ':START_ID', ':END_ID']

        headers.extend(self.extra)
        for prop in schema.sorted_properties:
            if prop.hidden or prop.type == registry.entity:
                continue
            headers.append(prop.name)
        writer.writerow(headers)

    def write_edges(self, proxy, extra):
        writer = self._get_writer(proxy.schema)
        # Thing is, one interval might connect more than one pair of nodes,
        # so we are unrolling them
        source_type = proxy.schema.get(proxy.schema.edge_source).type
        target_type = proxy.schema.get(proxy.schema.edge_target).type


        for (source, target) in proxy.edgepairs():
            type_ = proxy.schema.name.upper()

            source_id = self.get_id(source_type, source)
            target_id = self.get_id(target_type, source)

            # That potentially may lead to multiple edges with same id
            cells = [proxy.id, type_, source_id, target_id, proxy.caption]
            cells.extend(extra or [])

            for prop in proxy.schema.sorted_properties:
                if prop.hidden or prop.type == registry.entity:
                    continue
                cells.append(prop.type.join(proxy.get(prop)))

            writer.writerow(cells)

    def write_link(self, proxy, prop, value):
        if prop.type.name not in self.edge_types:
            return

        weight = prop.specificity(value)
        if weight == 0:
            return

        other_id = self.get_id(prop.type, value)
        if prop.type != registry.entity and other_id not in self.nodes_seen:
            row = [other_id, prop.type.name, prop.type.caption(value)]
            self.nodes_writer.writerow(row)
            self.nodes_seen.add(other_id)

        type_ = stringcase.constcase(prop.name)
        proxy_id = self.get_id(registry.entity, proxy.id)
        if proxy_id is None:
            return
        row = [type_, proxy_id, other_id, weight]
        self.links_writer.writerow(row)

    def write(self, proxy, extra=None):
        if proxy.schema.edge:
            return self.write_edges(proxy, extra)

        writer = self._get_writer(proxy.schema)
        proxy_id = self.get_id(registry.entity, proxy.id)
        if proxy_id is None:
            return
        label = ';'.join(ensure_list(proxy.schema.names))
        cells = [proxy_id, label, proxy.caption]
        cells.extend(extra or [])
        for prop in proxy.schema.sorted_properties:
            if prop.hidden or prop.type == registry.entity:
                continue
            cells.append(prop.type.join(proxy.get(prop)))
        writer.writerow(cells)

        for prop, values in proxy._properties.items():
            for value in ensure_list(values):
                self.write_link(proxy, prop, value)

    def finalize(self):
        script_path = self.directory.joinpath('neo4j_import.sh')
        with open(script_path, mode='w') as fp:
            cmd = '{} import --id-type=STRING --database={} \\\n'
            fp.write(cmd.format(NEO4J_ADMIN_PATH, NEO4J_DATABASE_NAME))
            fp.write('\t--multiline-fields=true \\\n')
            cmd = '\t--relationships={} \\\n'
            fp.write(cmd.format(os.path.basename(self.links_handler.name)))
            cmd = '\t--nodes={} \\\n'
            fp.write(cmd.format(os.path.basename(self.nodes_handler.name)))

            for schema, (handle, writer) in self.handles.items():
                file_name = os.path.basename(handle.name)
                if schema.edge:
                    cmd = '\t--relationships={} \\\n'
                    fp.write(cmd.format(file_name))
                else:
                    cmd = '\t--nodes={} \\\n'
                    fp.write(cmd.format(file_name))

        self.links_handler.close()
        self.nodes_handler.close()
        super().finalize()


class CypherGraphExporter(GraphExporter):
    """Cypher query format, used for import to Neo4J. This is a bit like
    writing SQL with individual statements - so for large datasets it
    might be a better idea to do a CSV-based import."""
    # https://www.opencypher.org/
    # MATCH (n) DETACH DELETE n;

    def __init__(self, fh, edge_types=DEFAULT_EDGE_TYPES):
        super(CypherGraphExporter, self).__init__(edge_types=edge_types)
        self.fh = fh

    def _to_map(self, data):
        values = []
        for key, value in data.items():
            value = '%s: %s' % (key, json.dumps(value))
            values.append(value)
        return ', '.join(values)

    def _make_node(self, attributes, label):
        node_id = attributes.get('id')
        if node_id is None:
            return
        cypher = 'MERGE (p { %(id)s }) ' \
                 'SET p += { %(map)s } SET p :%(label)s;\n'
        self.fh.write(cypher % {
            'id': self._to_map({'id': node_id}),
            'map': self._to_map(attributes),
            'label': ':'.join(ensure_list(label))
        })

    def _make_edge(self, source, target, attributes, type_):
        if source is None or target is None:
            return
        cypher = 'MATCH (s { %(source)s }), (t { %(target)s }) ' \
                 'MERGE (s)-[:%(type)s { %(map)s }]->(t);\n'
        self.fh.write(cypher % {
            'source': self._to_map({'id': source}),
            'target': self._to_map({'id': target}),
            'type': stringcase.constcase(type_),
            'map': self._to_map(attributes),
        })

    def write_edge(self, proxy, source, target, attributes):
        source = self.get_id(registry.entity, source)
        source_prop = proxy.schema.get(proxy.schema.edge_source)
        self._make_node({'id': source}, source_prop.range.name)

        target = self.get_id(registry.entity, target)
        target_prop = proxy.schema.get(proxy.schema.edge_target)
        self._make_node({'id': target}, target_prop.range.name)
        self._make_edge(source, target, attributes, proxy.schema.name)

    def write_node(self, proxy):
        node_id = self.get_id(registry.entity, proxy.id)
        attributes = self.get_attributes(proxy)
        attributes['caption'] = proxy.caption
        attributes['id'] = node_id
        self._make_node(attributes, proxy.schema.names)

    def write_link(self, proxy, prop, value, weight):
        node_id = self.get_id(registry.entity, proxy.id)
        other_id = self.get_id(prop.type, value)
        label = prop.type.name
        attributes = {'id': other_id}
        if prop.type == registry.entity and prop.range:
            label = prop.range.name
        else:
            attributes['caption'] = prop.type.caption(value)
        self._make_node(attributes, label)
        attributes = {'weight': weight}
        self._make_edge(node_id, other_id, attributes, prop.name)

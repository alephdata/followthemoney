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


class Neo4JCSVExporter(CSVExporter):
    def __init__(
        self,
        directory,
        dialect=csv.unix_dialect,
        extra=None,
        edge_types=DEFAULT_EDGE_TYPES,
    ):
        self.edge_types = edge_types
        super().__init__(directory, dialect, extra)

        self.links_handler, self.links_writer = self._open_csv_file('__links')
        self.links_writer.writerow([':START_ID', ':END_ID', 'weight'])

    def _write_header(self, writer, schema):
        headers = []

        if not schema.edge:
            headers = ['id:ID', ':LABEL']
        else:
            headers = ['id', ':TYPE']

        headers.extend(self.extra)

        source_prop = schema.get(schema.edge_source)
        target_prop = schema.get(schema.edge_target)

        for prop in schema.sorted_properties:
            if source_prop is not None and prop == source_prop:
                # TODO: check if we need/can add field name as well
                headers.append(':START_ID')
            elif target_prop is not None and prop == target_prop:
                headers.append(':END_ID')
            else:
                headers.append(prop.name)
        writer.writerow(headers)

    def write_edges(self, proxy, extra):
        writer = self._get_writer(proxy.schema)

        source_prop = proxy.schema.get(proxy.schema.edge_source)
        target_prop = proxy.schema.get(proxy.schema.edge_target)

        # Thing is, one interval might connect more than one pair of nodes,
        # so we are unrolling them
        for (source, target) in proxy.edgepairs():
            cells = [proxy.id, proxy.schema.name.upper()]
            cells.extend(extra or [])

            for prop in proxy.schema.sorted_properties:
                if prop == source_prop:
                    cells.append(source)
                elif prop == target_prop:
                    cells.append(target)
                else:
                    cells.append(prop.type.join(proxy.get(prop)))

            writer.writerow(cells)

    def write(self, proxy, extra=None):
        if proxy.schema.edge:
            # Exporting Interval descendants in a slighthly different manner
            self.write_edges(proxy, extra)
        else:
            writer = self._get_writer(proxy.schema)
            cells = [proxy.id, ';'.join(ensure_list(proxy.schema.names))]
            cells.extend(extra or [])
            for prop in proxy.schema.sorted_properties:
                cells.append(prop.type.join(proxy.get(prop)))
            writer.writerow(cells)

            for prop, values in proxy._properties.items():
                if prop.type.name not in self.edge_types:
                    continue
                for value in ensure_list(values):
                    weight = prop.specificity(value)
                    if weight == 0:
                        continue

                    self.links_writer.writerow([proxy.id, value, weight])

    def finalize(self):
        script_path = self.directory.joinpath('neo4j_import.sh')
        with open(script_path, mode='w') as fp:
            cmd = '{} import --id-type=STRING --database={} \\\n'
            fp.write(cmd.format(NEO4J_ADMIN_PATH, NEO4J_DATABASE_NAME))
            fp.write('--multiline-fields=true \\\n')
            cmd = '\t--relationships:LINKS={} \\\n'
            fp.write(cmd.format(os.path.basename(self.links_handler.name)))

            for schema, (handle, writer) in self.handles.items():
                file_name = os.path.basename(handle.name)
                if schema.edge:
                    cmd = '\t--relationships:{}={} \\\n'
                    fp.write(cmd.format(schema.name.upper(), file_name))
                else:
                    cmd = '\t--nodes:{}={} \\\n'
                    fp.write(cmd.format(schema.name, file_name))

        self.links_handler.close()
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
        cypher = 'MERGE (p { %(id)s }) ' \
                 'SET p += { %(map)s } SET p :%(label)s;\n'
        self.fh.write(cypher % {
            'id': self._to_map({'id': attributes.get('id')}),
            'map': self._to_map(attributes),
            'label': ':'.join(ensure_list(label))
        })

    def _make_edge(self, source, target, attributes, label):
        cypher = 'MATCH (s { %(source)s }), (t { %(target)s }) ' \
                 'MERGE (s)-[:%(label)s { %(map)s }]->(t);\n'
        label = [stringcase.constcase(l) for l in ensure_list(label)]
        self.fh.write(cypher % {
            'source': self._to_map({'id': source}),
            'target': self._to_map({'id': target}),
            'label': ':'.join(label),
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
        attributes['name'] = proxy.caption
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
            attributes['name'] = value
        self._make_node(attributes, label)
        attributes = {'weight': weight}
        self._make_edge(node_id, other_id, attributes, prop.name)

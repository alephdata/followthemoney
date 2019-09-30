import os
import csv
from pathlib import Path

from banal import ensure_list
from followthemoney.export.common import Exporter
from followthemoney.export.graph import DEFAULT_EDGE_TYPES


class CSVExporter(Exporter):
    def __init__(self, directory, dialect=csv.unix_dialect, extra=None):
        self.directory = Path(directory)
        self.dialect = dialect
        self.extra = extra or []
        self.handles = {}

    def _write_header(self, writer, schema):
        headers = ["id"]
        headers.extend(self.extra)
        for prop in schema.sorted_properties:
            # Not using label to make it more machine-readable:
            headers.append(prop.name)
        writer.writerow(headers)

    def _open_csv_file(self, name):
        self.directory.mkdir(parents=True, exist_ok=True)
        name = "{0}.csv".format(name)
        file_path = self.directory.joinpath(name)
        handle = open(file_path, mode="w")
        writer = csv.writer(handle, dialect=self.dialect)
        return handle, writer

    def _get_writer(self, schema):
        if schema not in self.handles:
            handle, writer = self._open_csv_file(schema.name)

            self.handles[schema] = (handle, writer)
            self._write_header(writer, schema)
        handle, writer = self.handles[schema]
        return writer

    def write(self, proxy, extra=None):
        writer = self._get_writer(proxy.schema)
        cells = [proxy.id]
        cells.extend(extra or [])
        for prop in proxy.schema.sorted_properties:
            cells.append(prop.type.join(proxy.get(prop)))
        writer.writerow(cells)

    def finalize(self):
        for (handle, writer) in self.handles.values():
            handle.close()


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

        self.links_handler, self.links_writer = self._open_csv_file("__links")
        self.links_writer.writerow([":START_ID", ":END_ID", "weight"])

    def _write_header(self, writer, schema):
        headers = []

        if not schema.edge:
            headers = ["id:ID", ":LABEL"]
        else:
            headers = ["id", ":TYPE"]

        headers.extend(self.extra)

        source_prop = schema.get(schema.edge_source)
        target_prop = schema.get(schema.edge_target)

        for prop in schema.sorted_properties:
            if source_prop is not None and prop == source_prop:
                # TODO: check if we need/can add field name as well
                headers.append(":START_ID")
            elif target_prop is not None and prop == target_prop:
                headers.append(":END_ID")
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
            cells = [proxy.id, ";".join(ensure_list(proxy.schema.names))]
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
        neo4j_admin_path = os.environ.get("NEO4J_ADMIN_PATH", "bin/neo4j-admin")
        neo4j_database_name = os.environ.get("NEO4J_DATABASE_NAME", "graph.db")

        with open(self.directory.joinpath("neo4j_import.sh"), mode="w") as fp:
            fp.write(
                "{} import --id-type=STRING --database={} \\\n".format(
                    neo4j_admin_path, neo4j_database_name
                )
            )
            fp.write("--multiline-fields=true \\\n")
            fp.write(
                "\t--relationships:LINKS={} \\\n".format(
                    os.path.basename(self.links_handler.name)
                )
            )

            for schema, (handle, writer) in self.handles.items():
                if schema.edge:
                    fp.write(
                        "\t--relationships:{}={} \\\n".format(
                            schema.name.upper(), os.path.basename(handle.name)
                        )
                    )
                else:
                    fp.write(
                        "\t--nodes:{}={} \\\n".format(
                            schema.name, os.path.basename(handle.name)
                        )
                    )

        self.links_handler.close()
        super().finalize()

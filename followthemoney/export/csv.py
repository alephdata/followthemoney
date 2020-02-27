import csv
from pathlib import Path
from banal import ensure_list

from followthemoney.export.common import Exporter


class CSVMixin(object):

    def _configure(self, directory, dialect=csv.unix_dialect, extra=None):
        self.directory = Path(directory)
        self.extra = ensure_list(extra)
        self.dialect = dialect
        self.handles = {}

    def _open_csv_file(self, name):
        self.directory.mkdir(parents=True, exist_ok=True)
        file_path = self.directory.joinpath('{0}.csv'.format(name))
        handle = open(file_path, mode='w')
        writer = csv.writer(handle, dialect=self.dialect)
        return handle, writer

    def _get_writer(self, schema):
        if schema not in self.handles:
            handle, writer = self._open_csv_file(schema.name)
            self.handles[schema] = (handle, writer)
            self._write_header(writer, schema)
        handle, writer = self.handles[schema]
        return writer

    def close(self):
        for (handle, writer) in self.handles.values():
            handle.close()


class CSVExporter(Exporter, CSVMixin):

    def __init__(self, directory, export_all=True, extra=None):
        Exporter.__init__(self, export_all=True)
        self._configure(directory, extra=extra)

    def _write_header(self, writer, schema):
        headers = ['id']
        headers.extend(self.extra)
        for prop in self.exportable_properties(schema):
            # Not using label to make it more machine-readable:
            headers.append(prop.name)
        writer.writerow(headers)

    def write(self, proxy, extra=None):
        writer = self._get_writer(proxy.schema)
        cells = [proxy.id]
        cells.extend(extra or [])
        for prop, values in self.exportable_fields(proxy):
            cells.append(prop.type.join(values))

        writer.writerow(cells)

    def finalize(self):
        self.close()

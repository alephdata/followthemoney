import csv
from pathlib import Path
from banal import ensure_list
from typing import Union, Optional, Dict, Tuple, Any, TextIO, Iterable

from followthemoney.export.common import Exporter
from followthemoney.schema import Schema
from followthemoney.proxy import EntityProxy


class CSVMixin(Exporter):

    def _configure(self, directory, dialect=csv.unix_dialect,
                   extra: Optional[str]=None):
        self.directory = Path(directory)
        self.extra = ensure_list(extra)
        self.dialect = dialect
        self.handles: Dict[Schema, Tuple[TextIO, Any]] = {}

    def _open_csv_file(self, name) -> Tuple[TextIO, Any]:
        self.directory.mkdir(parents=True, exist_ok=True)
        file_path = self.directory.joinpath('{0}.csv'.format(name))
        handle = open(file_path, mode='w')
        writer = csv.writer(handle, dialect=self.dialect)
        return handle, writer

    def _write_header(self, writer, schema: Schema):
        headers = ['id']
        headers.extend(self.extra)
        for prop in self.exportable_properties(schema):
            # Not using label to make it more machine-readable:
            headers.append(prop.name)
        writer.writerow(headers)

    def _get_writer(self, schema: Schema):
        if schema not in self.handles:
            handle, writer = self._open_csv_file(schema.name)
            self.handles[schema] = (handle, writer)
            self._write_header(writer, schema)
        handle, writer = self.handles[schema]
        return writer

    def close(self):
        for (handle, writer) in self.handles.values():
            handle.close()


class CSVExporter(CSVMixin):

    def __init__(self, directory: Union[Path, str], export_all: bool=True,
                 extra: Optional[str]=None):
        Exporter.__init__(self, export_all=True)
        self._configure(directory, extra=extra)

    def write(self, proxy: EntityProxy, extra: Optional[Iterable[str]]=None):  # type: ignore[override] # noqa
        writer = self._get_writer(proxy.schema)
        cells = [proxy.id]
        cells.extend(extra or [])
        for prop, values in self.exportable_fields(proxy):
            cells.append(prop.type.join(values))

        writer.writerow(cells)

    def finalize(self):
        self.close()

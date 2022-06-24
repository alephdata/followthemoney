import csv

try:
    from _csv import _writer as csv_writer
except ImportError:
    # Python 3.8/3.9 work-around:
    from _csv import writer as csv_writer  # type: ignore

from io import TextIOWrapper
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from followthemoney.proxy import E
from followthemoney.export.common import Exporter
from followthemoney.schema import Schema
from followthemoney.util import PathLike

CSVWriter = csv_writer


class CSVMixin(object):
    def _configure(
        self,
        directory: PathLike,
        extra: Optional[List[str]] = None,
    ) -> None:
        self.directory = Path(directory)
        self.extra = extra or []
        self.handles: Dict[Schema, Tuple[TextIOWrapper, CSVWriter]] = {}

    def _open_csv_file(self, name: str) -> Tuple[TextIOWrapper, CSVWriter]:
        self.directory.mkdir(parents=True, exist_ok=True)
        file_path = self.directory.joinpath("{0}.csv".format(name))
        handle = open(file_path, mode="w")
        writer = csv.writer(handle, dialect=csv.unix_dialect)
        return handle, writer

    def _write_header(self, writer: CSVWriter, schema: Schema) -> None:
        raise NotImplementedError

    def _get_writer(self, schema: Schema) -> CSVWriter:
        if schema not in self.handles:
            handle, writer = self._open_csv_file(schema.name)
            self.handles[schema] = (handle, writer)
            self._write_header(writer, schema)
        handle, writer = self.handles[schema]
        return writer

    def close(self) -> None:
        for (handle, _) in self.handles.values():
            handle.close()


class CSVExporter(Exporter, CSVMixin):
    def __init__(
        self,
        directory: PathLike,
        export_all: bool = True,
        extra: Optional[List[str]] = None,
    ) -> None:
        Exporter.__init__(self, export_all=export_all)
        self._configure(directory, extra=extra)

    def _write_header(self, writer: CSVWriter, schema: Schema) -> None:
        headers = ["id"]
        headers.extend(self.extra)
        for prop in self.exportable_properties(schema):
            # Not using label to make it more machine-readable:
            headers.append(prop.name)
        writer.writerow(headers)

    def write(self, proxy: E, extra: Optional[List[str]] = None) -> None:
        writer = self._get_writer(proxy.schema)
        cells = [proxy.id]
        cells.extend(extra or [])
        for prop, values in self.exportable_fields(proxy):
            cells.append(prop.type.join(values))

        writer.writerow(cells)

    def finalize(self) -> None:
        self.close()

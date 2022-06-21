from contextlib import contextmanager
import os
import json
import yaml
import click
import orjson
from pathlib import Path
from warnings import warn
from typing import Any, BinaryIO, Generator, Optional, TextIO, Type
from banal import is_mapping, is_listish, ensure_list

from followthemoney import model
from followthemoney.export.common import Exporter
from followthemoney.proxy import E, EntityProxy
from followthemoney.util import MEGABYTE, PathLike

MAX_LINE = 200 * MEGABYTE
InPath = click.Path(dir_okay=False, readable=True, path_type=Path, allow_dash=True)
OutPath = click.Path(dir_okay=False, writable=True, path_type=Path, allow_dash=True)


def write_object(stream: TextIO, obj: Any) -> None:
    warn("write_object() is deprecated.", DeprecationWarning, stacklevel=2)
    if hasattr(obj, "to_dict"):
        obj = obj.to_dict()
    data = json.dumps(obj)
    stream.write(data + "\n")


def write_entity(fh: BinaryIO, entity: E) -> None:
    data = entity.to_dict()
    entity_id = data.pop("id")
    assert entity_id is not None, data
    sort_data = dict(id=entity_id)
    sort_data.update(data)
    out = orjson.dumps(sort_data, option=orjson.OPT_APPEND_NEWLINE)
    fh.write(out)


def _read_one(data: Any, cleaned: bool = True) -> Generator[EntityProxy, None, None]:
    if is_mapping(data) and "schema" in data:
        yield model.get_proxy(data, cleaned=cleaned)


def read_entities(
    stream: TextIO, cleaned: bool = True, max_line: int = MAX_LINE
) -> Generator[EntityProxy, None, None]:
    warn("read_entities() is deprecated.", DeprecationWarning, stacklevel=2)
    while True:
        line = stream.readline(max_line)
        if not line:
            return
        data = json.loads(line)
        entities = ensure_list(data)
        if is_mapping(data):
            if "entities" in data:
                entities = data.get("entities", data)
            if "layout" in data:
                entities = data.get("layout", {}).get("entities", data)
        for entity in ensure_list(entities):
            yield from _read_one(entity, cleaned=cleaned)


def read_entity(
    stream: TextIO, cleaned: bool = True, max_line: int = MAX_LINE
) -> Optional[Any]:
    warn("read_entity() is deprecated.", DeprecationWarning, stacklevel=2)
    line = stream.readline(max_line)
    if not line:
        return None
    data = json.loads(line)
    for entity in _read_one(data, cleaned=cleaned):
        return entity
    return data


def binary_entities(
    fh: BinaryIO, entity_type: Type[E], cleaned: bool = True, max_line: int = MAX_LINE
) -> Generator[E, None, None]:
    while line := fh.readline(max_line):
        data = orjson.loads(line)
        yield entity_type.from_dict(model, data, cleaned=cleaned)


def path_entities(
    path: PathLike,
    entity_type: Type[E],
    cleaned: bool = True,
    max_line: int = MAX_LINE,
) -> Generator[E, None, None]:
    if str(path) == "-":
        fh = click.get_binary_stream("stdin")
        yield from binary_entities(fh, entity_type, cleaned=cleaned, max_line=max_line)
        return
    with open(path, "rb") as fh:
        yield from binary_entities(fh, entity_type, cleaned=cleaned, max_line=max_line)


@contextmanager
def path_writer(path: PathLike) -> Generator[BinaryIO, None, None]:
    """Open a file for writing binary content, or use stdout."""
    if str(path) == "-":
        yield click.get_binary_stream("stdout")
        return
    with open(path, "wb") as fh:
        yield fh


def export_stream(exporter: Exporter, path: Path) -> None:
    try:
        for entity in path_entities(path, EntityProxy):
            exporter.write(entity)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        exporter.finalize()


def load_mapping_file(file_path: PathLike) -> Any:
    """Load a YAML (or JSON) bulk load mapping file."""
    file_path = os.path.abspath(file_path)
    with open(file_path, "r") as fh:
        data = yaml.safe_load(fh) or {}
    return resolve_includes(file_path, data)


def resolve_includes(file_path: PathLike, data: Any) -> Any:
    """Handle include statements in the graph configuration file.

    This allows the YAML graph configuration to be broken into
    multiple smaller fragments that are easier to maintain."""
    if is_listish(data):
        return [resolve_includes(file_path, i) for i in data]
    if is_mapping(data):
        include_paths = ensure_list(data.pop("include", []))
        for include_path in include_paths:
            dir_prefix = os.path.dirname(file_path)
            include_path = os.path.join(dir_prefix, include_path)
            data.update(load_mapping_file(include_path))
        for key, value in data.items():
            data[key] = resolve_includes(file_path, value)
    return data

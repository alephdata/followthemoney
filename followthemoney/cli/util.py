import os
import json
import yaml
import click
from banal import is_mapping, is_listish, ensure_list

from followthemoney import model
from followthemoney.util import MEGABYTE

MAX_LINE = 200 * MEGABYTE


def write_object(stream, obj):
    if hasattr(obj, "to_dict"):
        obj = obj.to_dict()
    data = json.dumps(obj, sort_keys=True)
    stream.write(data + "\n")


def _read_one(data, cleaned=True):
    if is_mapping(data) and "schema" in data:
        yield model.get_proxy(data, cleaned=cleaned)


def read_entities(stream, cleaned=True, max_line=MAX_LINE):
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


def read_entity(stream, cleaned=True, max_line=MAX_LINE):
    line = stream.readline(max_line)
    if not line:
        return
    data = json.loads(line)
    for entity in _read_one(data, cleaned=cleaned):
        return entity
    return data


def export_stream(exporter, stream):
    try:
        while True:
            entity = read_entity(stream)
            if entity is None:
                break
            exporter.write(entity)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        exporter.finalize()


def load_mapping_file(file_path):
    """Load a YAML (or JSON) bulk load mapping file."""
    file_path = os.path.abspath(file_path)
    with open(file_path, "r") as fh:
        data = yaml.safe_load(fh) or {}
    return resolve_includes(file_path, data)


def resolve_includes(file_path, data):
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

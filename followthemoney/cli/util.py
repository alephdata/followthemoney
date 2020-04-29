import os
import json
import yaml
import click
from banal import is_mapping, is_listish, ensure_list

from followthemoney import model


def write_object(stream, obj):
    if hasattr(obj, 'to_dict'):
        obj = obj.to_dict()
    data = json.dumps(obj, sort_keys=True)
    stream.write(data + '\n')


def read_entity(stream):
    line = stream.readline()
    if not line:
        return
    data = json.loads(line)
    if is_mapping(data) and 'schema' in data:
        return model.get_proxy(data)
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
    with open(file_path, 'r') as fh:
        data = yaml.safe_load(fh) or {}
    return resolve_includes(file_path, data)


def resolve_includes(file_path, data):
    """Handle include statements in the graph configuration file.

    This allows the YAML graph configuration to be broken into
    multiple smaller fragments that are easier to maintain."""
    if is_listish(data):
        return [resolve_includes(file_path, i) for i in data]
    if is_mapping(data):
        include_paths = ensure_list(data.pop('include', []))
        for include_path in include_paths:
            dir_prefix = os.path.dirname(file_path)
            include_path = os.path.join(dir_prefix, include_path)
            data.update(load_mapping_file(include_path))
        for key, value in data.items():
            data[key] = resolve_includes(file_path, value)
    return data

import json
from banal import is_mapping

from followthemoney import model


def write_object(stream, obj):
    if hasattr(obj, 'to_dict'):
        obj = obj.to_dict()
    data = json.dumps(obj)
    stream.write(data + '\n')


def read_entity(stream):
    line = stream.readline()
    if not line:
        return
    data = json.loads(line)
    if is_mapping(data) and 'schema' in data:
        return model.get_proxy(data)
    return data

import json
import click
from banal import is_mapping

from followthemoney import model
from followthemoney_enrich import get_enricher, enricher_cache
from followthemoney_enrich.result import Result


def load_enricher(enricher):
    clazz = get_enricher(enricher)
    if clazz is None:
        raise click.BadParameter("Unknown enricher: %s" % enricher)
    enricher = clazz()
    enricher.cache = enricher_cache()
    return enricher


def write_object(stream, obj):
    if hasattr(obj, 'to_dict'):
        obj = obj.to_dict()
    data = json.dumps(obj)
    stream.write(data + '\n')


def read_object(stream):
    line = stream.readline()
    if not line:
        return
    data = json.loads(line)
    if is_mapping(data) and 'schema' in data:
        return model.get_proxy(data)
    if is_mapping(data) and 'enricher' in data:
        enricher = load_enricher(data.get('enricher'))
        return Result.from_dict(enricher, data)
    return data

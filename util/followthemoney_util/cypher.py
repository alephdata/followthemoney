import json
import click
import stringcase
from banal import ensure_list

from followthemoney.types import registry
from followthemoney_util.cli import cli
from followthemoney_util.util import read_object

# MATCH (n) DETACH DELETE n;

# MATCH (e:Thing {id: banana})
# MERGE ON MATCH SET e += {name: "Fox"};
# MERGE (p:Person { id: "banana" })
#     ON CREATE SET p = { name: "Banana" }
#     ON MATCH  SET p += { name: "Banana" };
# MERGE (p:Person { id: 5 })
#     SET p = { name: "Hedgehog" };


def _to_map(data):
    values = []
    for key, value in data.items():
        value = '%s: %s' % (key, json.dumps(value))
        values.append(value)
    return ', '.join(values)


def _to_labels(label):
    return ':'.join(ensure_list(label))


def _to_attributes(proxy, edge_types):
    attributes = {'id': proxy.id}
    for prop, values in proxy._properties.items():
        if prop.type not in edge_types:
            attributes[prop.name] = prop.type.join(values)
    return attributes


def _make_node(attributes, label):
    cypher = 'MERGE (p:%(label)s { %(id)s }) ' \
             'SET p += { %(map)s } SET p:%(label)s;'
    return cypher % {
        'id': _to_map({'id': attributes.get('id')}),
        'map': _to_map(attributes),
        'label': _to_labels(label)
    }


def _make_edge(source, target, attributes, label):
    cypher = 'MATCH (s { %(source)s }), (t { %(target)s }) ' \
             'MERGE (s)-[:%(label)s { %(map)s }]->(t);'
    label = [stringcase.constcase(l) for l in ensure_list(label)]
    return cypher % {
        'source': _to_map({'id': source}),
        'target': _to_map({'id': target}),
        'label': _to_labels(label),
        'map': _to_map(attributes),
    }


def _to_node(proxy, edge_types):
    node_id = registry.entity.rdf(proxy.id).n3()
    attributes = _to_attributes(proxy, edge_types)
    attributes['name'] = proxy.caption
    attributes['id'] = node_id
    yield _make_node(attributes, proxy.schema.names)

    for prop, values in proxy._properties.items():
        if prop.type not in edge_types:
            continue
        for value in ensure_list(values):
            weight = prop.type.specificity(value)
            if weight == 0:
                continue
            other_id = prop.type.rdf(value).n3()
            if prop.range:
                yield _make_node({'id': other_id}, prop.range.name)
            else:
                attributes = {'id': other_id, 'name': value}
                yield _make_node({'id': other_id}, prop.type.name)
            attributes = {'weight': weight}
            yield _make_edge(node_id, other_id, attributes, prop.name)


def _to_edge(proxy, edge_types):
    attributes = _to_attributes(proxy, edge_types)
    source_prop = proxy.schema.get(proxy.schema.edge_source)
    target_prop = proxy.schema.get(proxy.schema.edge_target)
    for (source, target) in proxy.edgepairs():
        source = registry.entity.rdf(source).n3()
        yield _make_node({'id': source}, source_prop.range.name)
        target = registry.entity.rdf(target).n3()
        yield _make_node({'id': target}, target_prop.range.name)
        yield _make_edge(source, target, attributes, proxy.schema.name)


def to_cypher(proxy, edge_types=(registry.entity,)):
    if proxy.schema.edge:
        yield from _to_edge(proxy, edge_types)
    else:
        yield from _to_node(proxy, edge_types)


@cli.command('export-cypher', help="Export to Cypher script")
def export_cypher():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            for cypher in to_cypher(entity):
                stdout.write(cypher)
                stdout.write('\n')
    except BrokenPipeError:
        pass

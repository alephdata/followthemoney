import json
import click

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object

# MATCH (e:Thing {id: banana})
# MERGE ON MATCH SET e += {name: "Fox"};
# MERGE (p:Person { id: "banana" })
#     ON CREATE SET p = { name: "Banana" }
#     ON MATCH  SET p += { name: "Banana" };
# MERGE (p:Person { id: 5 })
#     SET p = { name: "Hedgehog" };


def to_map(data):
    parts = ['{']
    for key, value in data.items():
        parts.extend((key, ':', json.dumps(value)))
    parts.append('}')
    return ' '.join(parts)


def convert_entity(entity):
    return 'banana'


@cli.command('export-cypher', help="Export to Cypher script")
def export_cypher():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            cypher = convert_entity(entity)
            stdout.write(cypher.decode('utf-8'))
            stdout.write('\n')
    except BrokenPipeError:
        pass

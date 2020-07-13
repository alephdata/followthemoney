import sys
import click
import logging
from rdflib import Graph, Namespace
from rdflib.namespace import SKOS, RDFS

from followthemoney import model

SCHEMA = Namespace("http://schema.org/")
PROP = Namespace("http://www.wikidata.org/prop/direct/")

ENTITY = "http://www.wikidata.org/entity/"
Q = Namespace(ENTITY)
SPECIAL = "https://www.wikidata.org/wiki/Special:EntityData/"

SCHEMATA = {Q["5"]: "Person"}

# Examples:
# spouse: https://www.wikidata.org/wiki/Property:P26
# father: https://www.wikidata.org/wiki/Property:P22
# member of: https://www.wikidata.org/wiki/Property:P463
# employer: https://www.wikidata.org/wiki/Property:P108
# bbc: https://www.wikidata.org/wiki/Q9531
# barack obama: https://www.wikidata.org/wiki/Q76
# siemens: https://www.wikidata.org/wiki/Q81230
# apple: https://www.wikidata.org/wiki/Q312


def parse_triples(fh, size=1000):
    while True:
        line = fh.readline()
        if not line:
            break
        try:
            graph = Graph()
            graph.parse(data=line, format="nt")
            yield from graph
        except Exception:
            pass


@click.command()
@click.option("-i", "--input", type=click.File("r"), default="-")  # noqa
def transform(input):
    prev = None
    entity = None
    for (s, p, o) in parse_triples(input):
        if s != prev and entity is not None:
            # print(entity.to_dict())
            pass
        if s != prev:
            prev = s
            if s.startswith(SPECIAL):
                qid = s[len(SPECIAL) :]
            else:
                qid = s[len(ENTITY) :]
            entity = model.make_entity("Thing")
            entity.make_id(qid)
            entity.add("wikidataId", qid)
            if s.startswith(ENTITY):
                entity.add("sourceUrl", str(s))

        if p in [SKOS.prefLabel, RDFS.label, SCHEMA.name]:
            entity.add("name", str(o))
            continue

        print(s, p, o)

        if p == PROP.P31:
            # print((p, o))
            pass


if __name__ == "__main__":
    fmt = "%(name)s [%(levelname)s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=fmt)
    transform()

from urllib import quote
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint  # noqa

from corpint.enrich.wikipedia import SITES

COUNTRIES = {}  # cache object
LINKS = {
    "P40": "child",
    "P26": "spouse",
    "P25": "mother",
    "P22": "father",
    "P43": "stepfather",
    "P44": "stepmother",
    "P1038": "relative",
    "P7": "brother",
    "P9": "sister",
    # 'P108': 'employer',
    # 'P102': 'party',
    # 'P463': 'member'
}
PROPERTIES = {
    "rdf-schema#label": "name",
    "description": "summary",
    "P569": "dob",
    "P734": "last_name",
    "P735": "first_name",
}

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")


def run_sparql(query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        yield result


def crawl_node(cid):
    query = "SELECT ?prop ?value WHERE { <%s> ?prop ?value . }" % cid
    for result in run_sparql(query):
        prop = result.get("prop").get("value")
        _, prop = prop.rsplit("/", 1)
        yield prop, result.get("value")


def get_country(uri):
    if uri not in COUNTRIES:
        for key, value in crawl_node(uri):
            if key in ["P901", "P297"]:
                COUNTRIES[uri] = value.get("value")
                break
    return COUNTRIES.get(uri)


def add_literal(data, value):
    if value.get("type") == "literal":
        lang = value.get("xml:lang", "en")
        data[lang] = value.get("value")
    else:
        for prop, val in crawl_node(value.get("value")):
            if prop in ["rdf-schema#label"]:
                lang = val.get("xml:lang", "en")
                data[lang] = val.get("value")
    return data


def pick_literal(data):
    for lang in ["en", "es", "fr", "de", "ru"]:
        if lang in data:
            return data[lang]
    for label in data.values():
        return label


def crawl_entity(emitter, cid, recurse=True):
    uid = emitter.uid(cid)
    if emitter.entity_exists(uid):
        return uid

    data = {"wikidata_id": cid, "uid": uid, "aliases": set()}
    for prop, value in crawl_node(cid):
        if prop in ["P27"]:
            if "/entity/statement/" in value.get("value"):
                for p, val in crawl_node(value.get("value")):
                    if p == prop:
                        value = val
            data["country"] = get_country(value.get("value"))
        elif prop in ["core#altLabel", "P742"]:
            for val in add_literal({}, value).values():
                data["aliases"].add(val)
        elif prop in PROPERTIES.keys():
            field = PROPERTIES.get(prop)
            if field is not None:
                if field not in data:
                    data[field] = {}
                add_literal(data[field], value)
        elif prop in LINKS.keys():
            if not recurse:
                continue
            if "/entity/statement/" in value.get("value"):
                for p, val in crawl_node(value.get("value")):
                    if p == prop:
                        value = val
            ouid = crawl_entity(emitter, value.get("value"), recurse=False)
            emitter.emit_link(
                {"source_uid": uid, "target_uid": ouid, "summary": LINKS.get(prop)}
            )

    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = pick_literal(value)

    emitter.log.info("Crawled [%(wikidata_id)s]: %(name)s", data)
    emitter.emit_entity(data)
    return uid


def enrich(origin, entity):
    # print entity
    for lang in SITES.keys():
        name = entity.data.get("wikipedia_%s" % lang)
        if name is None:
            continue
        slug = quote(name.encode("utf-8"))
        url = "https://%s.wikipedia.org/wiki/%s" % (lang, slug)
        query = "SELECT ?item WHERE { <%s> schema:about ?item . }" % url
        for result in run_sparql(query):
            cid = result.get("item").get("value")
            origin.log.info("Wikidata ID [%s]: %s", cid, entity.get("name"))
            emitter = origin.result(entity.uid, origin.uid(cid))
            uid = crawl_entity(emitter, cid)
            origin.emit_judgement(uid, entity.uid, True, decided=True)

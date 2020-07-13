# coding: utf-8
from hashlib import sha1
from pprint import pprint  # noqa
import mwclient

from corpint.model.schema import PERSON, OTHER


ORIGIN = "wikipedia"
SKIP_HOSTS = ["wikiquote", "simple.wiki", "commons.wiki", "collections.wiki"]
DISAMBIGUATION = [u"Шаблон:Неоднозначность", "Template:Disambiguation"]
SITES = {
    "en": mwclient.Site("en.wikipedia.org"),
    "ru": mwclient.Site("ru.wikipedia.org"),
}


def get_uid(page):
    uid = sha1(ORIGIN)
    uid.update(page.pagelanguage)
    uid.update(page.name.encode("utf-8"))
    return uid.hexdigest()


def page_url(page):
    slug = page.normalize_title(page.name)
    return "http://%s/wiki/%s" % (page.site.host, slug)


def page_entity(emitter, page, path=None):
    if not page.page_title:
        return

    if path is None:
        path = []

    path.append(page.pagelanguage)

    for host in SKIP_HOSTS:
        if host in page.site.host:
            emitter.log.info("Skip [%s]: %s", page.site.host, page.page_title)
            return

    if page.pagelanguage not in SITES.keys():
        emitter.log.info("Skip [%s]: %s", page.site.host, page.page_title)
        return

    while page.redirect:
        page = page.redirects_to()

    for template in page.templates():
        if template.name not in DISAMBIGUATION:
            continue
        emitter.log.warning("Disambiguation page: %s", page.name)
        return

    uid = emitter.uid(page.pagelanguage, page.name)
    aliases = set()

    if emitter.entity_exists(uid):
        emitter.log.info("Done [%s]: %s", page.site.host, page.page_title)
        return uid

    emitter.log.info("Crawl [%s]: %s", page.site.host, page.page_title)

    for lsite, lemma in page.langlinks():
        aliases.add(lemma)
        site = SITES.get(lsite)
        if site is not None and lsite not in path:
            opage = site.Pages[lemma]
            ouid = page_entity(emitter, opage, path=path)
            emitter.emit_judgement(uid, ouid, True, decided=True)

    for bl in page.backlinks(redirect=True):
        if not bl.redirect:
            continue
        if bl.redirects_to().page_title == page.page_title:
            aliases.add(bl.page_title)

    emitter.emit_entity(
        {
            "uid": uid,
            "wikipedia_" + page.pagelanguage: page.name,
            "name": page.page_title,
            "aliases": aliases,
        }
    )
    return uid


def enrich(origin, entity):
    # Assume entries on companies in Wikipedia are pretty useless.
    if entity.schema not in [PERSON, OTHER]:
        return

    for lang, site in SITES.items():
        origin.log.info("Search [%s]: %s", lang, entity["name"])
        for name in entity.names:
            for res in site.search(name, what="nearmatch", limit=5):
                page = site.Pages[res.get("title")]
                match_uid = origin.uid(page.pagelanguage, page.name)
                emitter = origin.result(entity.uid, match_uid)
                page_entity(emitter, page)

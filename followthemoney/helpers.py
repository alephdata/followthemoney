# This module violates the boundary between the role of code and
# YAML in the rest of followthemoney. It handles normalisations
# which would be much harder to express in abstract, especially
# those thet simplify the data based on their pragmatics.
#
# If anyone were to swap out the default model, this would
# probably be the first place to break.
from os.path import splitext
from typing import Iterable, List, Optional
from normality import safe_filename
from mimetypes import guess_extension
from itertools import product

from followthemoney.types import registry
from followthemoney.proxy import EntityProxy
from followthemoney.util import join_text

PROV_MIN_DATES = ("createdAt", "authoredAt", "publishedAt")
PROV_MAX_DATES = ("modifiedAt", "retrievedAt")


def remove_checksums(proxy: EntityProxy) -> EntityProxy:
    """When accepting entities via a web API, it would consistute
    a security risk to allow a user to submit checksum-type properties.
    These can be traded in for access to said files if they exist in the
    underlying content-addressed storage. It seems safest to just remove
    all checksums from entities when they are untrusted user input."""
    for prop in proxy.iterprops():
        if prop.type == registry.checksum:
            proxy.pop(prop)
    return proxy


def simplify_provenance(proxy: EntityProxy) -> EntityProxy:
    """If there are multiple dates given for some of the provenance
    fields, we can logically conclude which one is the most meaningful."""
    for prop_name in PROV_MAX_DATES:
        values = proxy.pop(prop_name, quiet=True)
        if len(values):
            proxy.set(prop_name, max(values), cleaned=True)
    for prop_name in PROV_MIN_DATES:
        values = proxy.pop(prop_name, quiet=True)
        if len(values):
            proxy.set(prop_name, min(values), cleaned=True)
    return proxy


def entity_filename(
    proxy: EntityProxy, base_name: Optional[str] = None, extension: Optional[str] = None
) -> Optional[str]:
    """Derive a safe filename for the given entity."""
    if proxy.schema.is_a("Document"):
        for extension_ in proxy.get("extension", quiet=True):
            if extension is not None:
                break
            extension = extension_
        for file_name in proxy.get("fileName", quiet=True):
            base_name_, extension_ = splitext(file_name)
            if base_name is None and len(base_name_):
                base_name = base_name_
            if extension is None and len(extension_):
                extension = extension_
        for mime_type in proxy.get("mimeType", quiet=True):
            if extension is not None:
                break
            extension = guess_extension(mime_type)
    base_name = base_name or proxy.id
    return safe_filename(base_name, extension=extension)


def name_entity(entity: EntityProxy) -> EntityProxy:
    """If an entity has multiple names, pick the most central one
    and set all the others as aliases. This is awkward given that
    names are not special and may not always be the caption."""
    if entity.schema.is_a("Thing"):
        names = entity.get("name")
        if len(names) > 1:
            name = registry.name.pick(names)
            if name in names:
                names.remove(name)
            entity.set("name", name)
            entity.add("alias", names)
    return entity


def remove_prefix_dates(entity: EntityProxy) -> EntityProxy:
    """If an entity has multiple values for a date field, you may
    want to remove all those that are prefixes of others. For example,
    if a Person has both a birthDate of 1990 and of 1990-05-01, we'd
    want to drop the mention of 1990."""
    for prop in entity.iterprops():
        if prop.type == registry.date:
            values = remove_prefix_date_values(entity.get(prop))
            entity.set(prop, values)
    return entity


def remove_prefix_date_values(values: Iterable[str]) -> List[str]:
    """See ``remove_prefix_dates``."""
    kept: List[str] = []
    values = sorted(values, key=len, reverse=True)
    for index, value in enumerate(values):
        keep = True
        for longer in values[:index]:
            if longer.startswith(value):
                keep = False
                break
        if keep:
            kept.append(value)
    return kept


def inline_names(entity: EntityProxy, related: EntityProxy) -> None:
    """Attempt to solve a weird UI problem. Imagine we are showing a list of
    payments between a sender and a beneficiary to a user. They may now conduct
    a search for a term present in the sender or recipient name, but there will
    be no result, because the name is only indexed with the parties, but not in
    the payment. This is part of a partial work-around to that.

    This is really bad in theory, but really useful in practice. Shoot me.
    """
    prop = entity.schema.get("namesMentioned")
    if prop is not None:
        entity.add(prop, related.get_type_values(registry.name))


def combine_names(entity: EntityProxy) -> EntityProxy:
    """This function will try to build names from name parts provided as part
    of a person entity. This is of course impossible to do culturally correctly
    for the whole planet at once, so it should be mostly used for internal-facing
    (e.g. matching) processes."""
    if entity.schema.is_a("Person"):
        first_names = entity.get("firstName")
        second_names = entity.get("secondName")
        second_names.append("")
        middle_names = entity.get("middleName")
        middle_names.append("")
        father_names = entity.get("fatherName")
        father_names.append("")
        last_names = entity.get("lastName")
        for (first, second, middle, father, last) in product(
            first_names, second_names, middle_names, father_names, last_names
        ):
            name = join_text(first, second, middle, father, last)
            if name is not None:
                entity.add("alias", name)

        # If no first name is given, at least add the last name:
        if not entity.get_type_values(registry.name) and len(last_names):
            entity.add("alias", last_names)
    return entity

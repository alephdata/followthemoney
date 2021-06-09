# This module violates the boundary between the role of code and
# YAML in the rest of followthemoney. It handles normalisations
# which would be much harder to express in abstract, especially
# those thet simplify the data based on their pragmatics.
#
# If anyone were to swap out the default model, this would
# probably be the first place to break.
from os.path import splitext
from normality import safe_filename
from mimetypes import guess_extension

from followthemoney.types import registry


def remove_checksums(proxy):
    """When accepting entities via a web API, it would consistute
    a security risk to allow a user to submit checksum-type properties.
    These can be traded in for access to said files if they exist in the
    underlying content-addressed storage. It seems safest to just remove
    all checksums from entities when they are untrusted user input."""
    for prop in proxy.iterprops():
        if prop.type == registry.checksum:
            proxy.pop(prop)
    return proxy


def simplify_provenance(proxy):
    """If there are multiple dates given for some of the provenance
    fields, we can logically conclude which one is the most meaningful."""
    for prop_name in ["modifiedAt", "retrievedAt"]:
        if proxy.has(prop_name, quiet=True):
            values = proxy.get(prop_name)
            proxy.set(prop_name, max(values))
    for prop_name in ["authoredAt", "publishedAt"]:
        if proxy.has(prop_name, quiet=True):
            values = proxy.get(prop_name)
            proxy.set(prop_name, min(values))
    return proxy


def entity_filename(proxy, base_name=None, extension=None):
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


def name_entity(entity):
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


def remove_prefix_dates(entity):
    """If an entity has multiple values for a date field, you may
    want to remove all those that are prefixes of others. For example,
    if a Person has both a birthDate of 1990 and of 1990-05-01, we'd
    want to drop the mention of 1990."""
    for prop in entity.iterprops():
        if prop.type == registry.date:
            values = remove_prefix_date_values(entity.get(prop))
            entity.set(prop, values)
    return entity


def remove_prefix_date_values(values):
    """See ``remove_prefix_dates``."""
    kept = []
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


def inline_names(entity, related):
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

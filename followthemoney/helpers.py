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
    a security risk to allow a user to submit checksum-type properties
    because these can be traded in for access to said files if they
    exist in the underlying content-addressed storage. Thus it seems
    safest to just remove all checksums from entities when they are
    untrusted user input.
    """
    for prop in proxy.iterprops():
        if prop.type == registry.checksum:
            proxy.pop(prop)
    return proxy


def simplify_provenance(proxy):
    """If there are multiple dates given for some of the provenance
    fields, we can logically conclude which one is the most meaningful."""
    for prop_name in ['modifiedAt', 'retrievedAt']:
        if proxy.has(prop_name, quiet=True):
            values = proxy.get(prop_name)
            proxy.set(prop_name, max(values))
    for prop_name in ['authoredAt', 'publishedAt']:
        if proxy.has(prop_name, quiet=True):
            values = proxy.get(prop_name)
            proxy.set(prop_name, min(values))
    return proxy


def entity_filename(proxy, base_name=None, extension=None):
    """Derive a safe filename for the given entity."""
    if proxy.schema.is_a('Document'):
        for extension_ in proxy.get('extension', quiet=True):
            if extension is not None:
                break
            extension = extension_
        for file_name in proxy.get('fileName', quiet=True):
            base_name_, extension_ = splitext(file_name)
            if base_name is None and len(base_name_):
                base_name = base_name_
            if extension is None and len(extension_):
                extension = extension_
        for mime_type in proxy.get('mimeType', quiet=True):
            if extension is not None:
                break
            extension = guess_extension(mime_type)
    base_name = base_name or proxy.id
    return safe_filename(base_name, extension=extension)


def name_entity(entity):
    """If an entity has multiple names, pick the most central one
    and set all the others as aliases. This is awkward given that
    names aren't special and may not always be the caption."""
    if entity.schema.is_a('Thing'):
        names = entity.get('name')
        if len(names) > 1:
            name = registry.name.pick(names)
            if name in names:
                names.remove(name)
            entity.set('name', name)
            entity.add('alias', names)
    return entity

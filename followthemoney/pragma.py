# This module violates the boundary between the role of code and
# YAML in the rest of followthemoney. It handles normalisations
# which would be much harder to express in abstract, especially
# those thet simplify the data based on their pragmatics.
#
# If anyone were to swap out the default model radically, this would
# probably be the first place to break.

# from followthemoney import model
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
            proxy.pop(prop, quiet=True)
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


def cleanup(proxy):
    """Apply all pragma cleanups to a proxy."""
    proxy = remove_checksums(proxy)
    proxy = simplify_provenance(proxy)
    return proxy

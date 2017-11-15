import six
from normality import stringify
from banal import clean_dict, unique_list, is_sequence


def key_bytes(key):
    """Convert the given data to a value appropriate for hashing."""
    key = stringify(key)
    if key is None:
        return six.binary_type()
    return key.encode('utf-8')


def merge_data(old, new):
    """Exend the values of the new doc with extra values from the old."""
    if old is None or new is None:
        return old or new
    old = dict(clean_dict(old))
    new = dict(clean_dict(new))
    for k, v in new.items():
        if k in old:
            if is_sequence(v):
                v = old[k] + v
                old[k] = unique_list(v)
            elif isinstance(v, dict):
                old[k] = merge_data(v, old[k])
        else:
            old[k] = v
    return old

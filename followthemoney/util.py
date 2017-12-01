import six
from normality import stringify
from banal import is_mapping, is_sequence
from banal import unique_list, ensure_list


def key_bytes(key):
    """Convert the given data to a value appropriate for hashing."""
    key = stringify(key)
    if key is None:
        return six.binary_type()
    return key.encode('utf-8')


def merge_data(old, new):
    """Extend the values of the new doc with extra values from the old."""
    if is_sequence(old) or is_sequence(new):
        new = ensure_list(new)
        new.extend(ensure_list(old))
        if not len(new):
            return None
        return unique_list(new)
    if is_mapping(old) or is_mapping(new):
        old = old if is_mapping(old) else {}
        new = new if is_mapping(new) else {}
        keys = set(new.keys())
        keys.update(old.keys())
        combined = {}
        for key in keys:
            value = merge_data(old.get(key), new.get(key))
            if value is not None:
                combined[key] = value
        return combined
    return new or old

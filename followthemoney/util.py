import six
from normality import stringify
from normality.cleaning import remove_control_chars


def key_bytes(key):
    """Convert the given data to a value appropriate for hashing."""
    key = stringify(key)
    if key is None:
        return six.binary_type()
    key = remove_control_chars(key)
    return key.encode('utf-8')

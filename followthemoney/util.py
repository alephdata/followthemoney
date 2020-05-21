import os
import logging
from babel import Locale
from gettext import translation
from rdflib import Namespace
from threading import local
from normality import stringify
from normality.cleaning import compose_nfc
from normality.cleaning import remove_unsafe_chars
from normality.encoding import DEFAULT_ENCODING
from banal import is_mapping, unique_list, ensure_list

NS = Namespace('https://w3id.org/ftm#')
MEGABYTE = 1024 * 1024
DEFAULT_LOCALE = 'en'
i18n_path = os.path.join(os.path.dirname(__file__), 'translations')
state = local()
log = logging.getLogger(__name__)


def gettext(*args, **kwargs):
    if not hasattr(state, 'translation'):
        set_model_locale(DEFAULT_LOCALE)
    return state.translation.gettext(*args, **kwargs)


def defer(text):
    return text


def set_model_locale(locale):
    state.locale = locale
    state.translation = translation('followthemoney', i18n_path, [locale],
                                    fallback=True)


def get_locale():
    if not hasattr(state, 'locale'):
        return Locale(DEFAULT_LOCALE)
    return Locale(state.locale)


def get_env_list(name, default=[]):
    value = stringify(os.environ.get(name))
    if value is not None:
        values = value.split(':')
        if len(values):
            return values
    return default


def sanitize_text(text, encoding=DEFAULT_ENCODING):
    text = stringify(text, encoding_default=encoding)
    if text is not None:
        try:
            text = compose_nfc(text)
        except (SystemError, Exception) as ex:
            log.warning("Cannot NFC text: %s", ex)
            return None
        text = remove_unsafe_chars(text)
        text = text.encode(DEFAULT_ENCODING, 'replace')
        return text.decode(DEFAULT_ENCODING, 'replace')


def key_bytes(key):
    """Convert the given data to a value appropriate for hashing."""
    if isinstance(key, bytes):
        return key
    key = stringify(key) or ''
    return key.encode('utf-8')


def get_entity_id(obj):
    """Given an entity-ish object, try to get the ID."""
    if is_mapping(obj):
        obj = obj.get('id')
    elif hasattr(obj, 'id'):
        obj = obj.id
    return sanitize_text(obj)


def merge_context(left, right):
    """When merging two entities, we make lists of all the
    duplicate context keys."""
    combined = {}
    keys = [*left.keys(), *right.keys()]
    for key in set(keys):
        lval = ensure_list(left.get(key))
        rval = ensure_list(right.get(key))
        combined[key] = unique_list([*lval, *rval])
    return combined


def dampen(short, long, text):
    length = len(text) - short
    baseline = max(1.0, (long - short))
    return max(0, min(1.0, (length / baseline)))


def shortest(*texts):
    return min(texts, key=len)

import os
from threading import local
from normality import stringify
from babel import Locale
from gettext import translation
from rdflib import Namespace
from banal import is_mapping, is_sequence
from banal import unique_list, ensure_list

NS = Namespace('https://w3id.org/ftm#')
MEGABYTE = 1024 * 1024
DEFAULT_LOCALE = 'en'
i18n_path = os.path.join(os.path.dirname(__file__), 'translations')
state = local()


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
    return stringify(obj)


def merge_data(old, new):
    """Extend the values of the new doc with extra values from the old."""
    if is_sequence(old) or is_sequence(new):
        new = ensure_list(new)
        new.extend(ensure_list(old))
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


def dampen(short, long, text):
    length = len(text) - short
    baseline = max(1.0, (long - short))
    return max(0, min(1.0, (length / baseline)))


def shortest(*texts):
    return min(texts, key=len)

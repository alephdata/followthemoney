import os
import logging
from threading import local
from rdflib import Identifier  # type: ignore
from typing import Any, Union, List, Optional, Dict, Tuple, Mapping
from typing import TYPE_CHECKING

from normality import stringify  # type: ignore
from normality.cleaning import compose_nfc  # type: ignore
from normality.cleaning import remove_unsafe_chars
from normality.encoding import DEFAULT_ENCODING  # type: ignore
from babel import Locale  # type: ignore
from gettext import translation
from rdflib import Namespace  # type: ignore
from banal import is_mapping, is_sequence
from banal import unique_list, ensure_list

NS = Namespace('https://w3id.org/ftm#')
MEGABYTE = 1024 * 1024
DEFAULT_LOCALE = 'en'
i18n_path = os.path.join(os.path.dirname(__file__), 'translations')
state = local()
log = logging.getLogger(__name__)

# Type aliases:
if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy

TripleType = Tuple[Identifier, Identifier, Identifier]
ProxyData = Union[EntityProxy, Mapping]


def gettext(*args, **kwargs):
    if not hasattr(state, 'translation'):
        set_model_locale(DEFAULT_LOCALE)
    return state.translation.gettext(*args, **kwargs)


def defer(text: Any) -> Any:
    return text


def set_model_locale(locale):
    state.locale = locale
    state.translation = translation('followthemoney', i18n_path, [locale],
                                    fallback=True)


def get_locale() -> Locale:
    if not hasattr(state, 'locale'):
        return Locale(DEFAULT_LOCALE)
    return Locale(state.locale)


def get_env_list(name, default=[]) -> List[str]:
    value = stringify(os.environ.get(name))
    if value is not None:
        values = value.split(':')
        if len(values):
            return values
    return default


def sanitize_text(text: Any, encoding=DEFAULT_ENCODING) -> Optional[str]:
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
    return None


def key_bytes(key: Union[bytes, Any]) -> bytes:
    """Convert the given data to a value appropriate for hashing."""
    if isinstance(key, bytes):
        return key
    key = stringify(key) or ''
    return key.encode('utf-8')


def get_entity_id(obj: Any) -> Optional[str]:
    """Given an entity-ish object, try to get the ID."""
    if is_mapping(obj):
        obj = obj.get('id')
    elif hasattr(obj, 'id'):
        obj = obj.id
    return sanitize_text(obj)


def merge_data(old, new) -> Union[List, Dict]:
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


def dampen(short: float, long: float, text: str) -> float:
    length = len(text) - short
    baseline = max(1.0, (long - short))
    return max(0, min(1.0, (length / baseline)))


def shortest(*texts) -> str:
    return min(texts, key=len)

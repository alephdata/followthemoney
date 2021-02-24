import os
import logging
from hashlib import sha1
from babel import Locale  # type: ignore
from gettext import translation
from rdflib import Namespace  # type: ignore
from threading import local
from typing import cast, Dict, Any, List, Optional, TypeVar, Union, Sequence
from normality import stringify
from normality.cleaning import compose_nfc
from normality.cleaning import remove_unsafe_chars
from normality.encoding import DEFAULT_ENCODING
from banal import is_mapping, unique_list, ensure_list

NS = Namespace("https://w3id.org/ftm#")
MEGABYTE = 1024 * 1024
DEFAULT_LOCALE = "en"
i18n_path = os.path.join(os.path.dirname(__file__), "translations")
state = local()
log = logging.getLogger(__name__)
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def gettext(*args: str, **kwargs: Dict[str, str]) -> str:
    if not hasattr(state, "translation"):
        set_model_locale(DEFAULT_LOCALE)
    return cast(str, state.translation.gettext(*args, **kwargs))


def defer(text: str) -> str:
    return text


def set_model_locale(locale: Locale) -> None:
    state.locale = locale
    state.translation = translation(
        "followthemoney", i18n_path, [locale], fallback=True
    )


def get_locale() -> Locale:
    if not hasattr(state, "locale"):
        return Locale(DEFAULT_LOCALE)
    return Locale(state.locale)


def get_env_list(name: str, default: List[str] = []) -> List[str]:
    value = stringify(os.environ.get(name))
    if value is not None:
        values = value.split(":")
        if len(values):
            return values
    return default


def sanitize_text(text: Any, encoding: str = DEFAULT_ENCODING) -> Optional[str]:
    text = stringify(text, encoding_default=encoding)
    if text is None:
        return None
    try:
        text = compose_nfc(text)
    except (SystemError, Exception) as ex:
        log.warning("Cannot NFC text: %s", ex)
        return None
    text = remove_unsafe_chars(text)
    if text is None:
        return None
    byte_text = text.encode(DEFAULT_ENCODING, "replace")
    return cast(str, byte_text.decode(DEFAULT_ENCODING, "replace"))


def value_list(value: Union[T, Sequence[T]]) -> List[T]:
    if not isinstance(value, (str, bytes)):
        try:
            return [v for v in cast(Sequence[T], value)]
        except TypeError:
            pass
    return [cast(T, value)]


def key_bytes(key: Any) -> bytes:
    """Convert the given data to a value appropriate for hashing."""
    if isinstance(key, bytes):
        return key
    key = stringify(key)
    if key is None:
        return b""
    return cast(bytes, key.encode("utf-8"))


def get_entity_id(obj: Any) -> Optional[str]:
    """Given an entity-ish object, try to get the ID."""
    if is_mapping(obj):
        obj = obj.get("id")
    else:
        try:
            obj = obj.id
        except AttributeError:
            pass
    return stringify(obj)


def make_entity_id(*parts: Any, key_prefix: Optional[str] = None) -> Optional[str]:
    digest = sha1()
    if key_prefix:
        digest.update(key_bytes(key_prefix))
    base = digest.digest()
    for part in parts:
        digest.update(key_bytes(part))
    if digest.digest() == base:
        return None
    return digest.hexdigest()


def merge_context(left: Dict[K, V], right: Dict[K, V]) -> Dict[K, List[V]]:
    """When merging two entities, we make lists of all the
    duplicate context keys."""
    combined = {}
    keys = [*left.keys(), *right.keys()]
    for key in set(keys):
        lval: List[V] = ensure_list(left.get(key))
        rval: List[V] = ensure_list(right.get(key))
        combined[key] = unique_list([*lval, *rval])
    return combined


def dampen(short: int, long: int, text: str) -> float:
    length = len(text) - short
    baseline = max(1.0, (long - short))
    return max(0, min(1.0, (length / baseline)))


def shortest(*texts: str) -> str:
    return min(texts, key=len)

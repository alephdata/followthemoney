from functools import cache
from typing import Any, List, Mapping, Sequence, Tuple

from followthemoney.model import Model
from followthemoney.util import sanitize_text

BASE_ID = "id"


def pack_prop(schema: str, prop: str) -> str:
    return f"{schema}:{prop}"


@cache
def get_prop_type(schema: str, prop: str) -> str:
    if prop == BASE_ID:
        return BASE_ID
    schema_obj = Model.instance().get(schema)
    if schema_obj is None:
        raise TypeError("Schema not found: %s" % schema)
    prop_obj = schema_obj.get(prop)
    if prop_obj is None:
        raise TypeError("Property not found: %s" % prop)
    return prop_obj.type.name


@cache
def unpack_prop(id: str) -> Tuple[str, str, str]:
    schema, prop = id.split(":", 1)
    prop_type = get_prop_type(schema, prop)
    return schema, prop_type, prop


def string_list(value: Any) -> List[str]:
    """Convert a value to a list of strings."""
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        text = sanitize_text(value)
        if text is None:
            return []
        return [text]
    if not isinstance(value, (Sequence, set)):
        value = [value]
    texts: List[str] = []
    for inner in value:
        if isinstance(inner, Mapping):
            text = inner.get("id")
            if text is not None:
                texts.append(text)
            continue

        try:
            texts.append(inner.id)
            continue
        except AttributeError:
            pass

        text = sanitize_text(inner)
        if text is not None:
            texts.append(text)

    return texts

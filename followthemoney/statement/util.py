from functools import cache
from typing import Tuple

from followthemoney.model import Model

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

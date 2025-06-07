from normality import stringify, slugify
from prefixdate import parse as prefix_parse
from typing import Any, Dict, List, Optional

from followthemoney.types import registry
from followthemoney.types.common import PropertyType
from followthemoney.exc import MetadataException


def type_check(type_: PropertyType, value: Any) -> Optional[str]:
    text = stringify(value)
    if text is None:
        return None
    cleaned = type_.clean_text(text)
    if cleaned is None:
        raise MetadataException("Invalid %s: %r" % (type_.name, value))
    return cleaned


def type_require(type_: PropertyType, value: Any) -> str:
    """Check that the given metadata field is a valid string of the given FtM property type."""
    text = stringify(value)
    if text is None:
        raise MetadataException("Invalid %s: %r" % (type_.name, value))
    cleaned = type_.clean_text(text)
    if cleaned is None:
        raise MetadataException("Invalid %s: %r" % (type_.name, value))
    return cleaned


def datetime_check(value: Any) -> Optional[str]:
    """Check that the given metadata field is a valid datetime."""
    return prefix_parse(value).text


def int_check(value: Any) -> Optional[int]:
    """Check that the given metadata field is a valid integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def dataset_name_check(value: Any) -> str:
    """Check that the given value is a valid dataset name. This doesn't convert
    or clean invalid names, but raises an error if they are not compliant to
    force the user to fix an invalid name"""
    cleaned = type_require(registry.string, value)
    if slugify(cleaned, sep="_") != cleaned:
        raise MetadataException("Invalid %s: %r" % ("dataset name", value))
    return cleaned


def string_list(value: Any) -> List[str]:
    if value is None:
        return []
    return [type_require(registry.string, s) for s in value]


def cleanup(data: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in list(data.items()):
        if value is None:
            data.pop(key)
    return data


class Named(object):
    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other: Any) -> bool:
        try:
            return not not self.name == other.name
        except AttributeError:
            return False

    def __lt__(self, other: Any) -> bool:
        return self.name.__lt__(other.name)

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name!r})>"

import json
from typing import Any, Optional, Sequence, TYPE_CHECKING
from banal import ensure_list

from followthemoney.types.common import PropertyType
from followthemoney.util import sanitize_text, defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class JsonType(PropertyType):
    """An encoded JSON object. This is used to store raw HTTP headers for documents
    and some other edge cases. It's a really bad idea and we should try to get rid
    of JSON properties."""

    name = "json"
    group = None
    label = _("Nested data")
    plural = _("Nested data")
    matchable = False

    def pack(self, obj: Any) -> Optional[str]:
        """Encode a given value to JSON."""
        # TODO: use a JSON encoder that handles more types?
        if obj is None:
            return None
        return json.dumps(obj)

    def unpack(self, obj: str) -> Any:
        """Decode a given JSON object."""
        try:
            return json.loads(obj)
        except Exception:
            return obj

    def clean(
        self,
        raw: Any,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        if not isinstance(raw, str):
            return self.pack(raw)
        else:
            return sanitize_text(raw)

    def join(self, values: Sequence[str]) -> str:
        """Turn multiple values into a JSON array."""
        values = [self.unpack(v) for v in ensure_list(values)]
        data = self.pack(values)
        if data is None:
            return "[]"
        return data

    def node_id(self, value: str) -> None:
        return None

import json  # yay Python 3
from banal import ensure_list
from typing import Optional, Any, Iterable, List

from followthemoney.types.common import PropertyType
from followthemoney.util import sanitize_text, defer as _


class JsonType(PropertyType):
    name: str = 'json'
    group: Optional[str] = None
    label: str = _('Nested data')
    matchable: bool = False

    def pack(self, obj: Any) -> Optional[str]:
        """Encode a given value to JSON."""
        # TODO: use a JSON encoder that handles more types?
        if obj is not None:
            return json.dumps(obj)
        return None

    def unpack(self, obj: str) -> Any:
        """Decode a given JSON object."""
        if obj is None:
            return None
        try:
            return json.loads(obj)
        except Exception:
            return obj

    def clean(self, obj: Any, **kwargs) -> Optional[str]:  # type: ignore[override] # noqa
        if not isinstance(obj, str):
            _obj = self.pack(obj)
        else:
            _obj = sanitize_text(obj)
        return _obj

    def normalize(self, obj: Any, cleaned: bool = False,
                  **kwargs) -> List:  # type: ignore[override] # noqa
        return [] if obj is None else [obj]

    def join(self, values: Iterable[Any]) -> Optional[str]:  # type: ignore[override] # noqa
        """Turn multiple values into a JSON array."""
        values = [self.unpack(v) for v in ensure_list(values)]
        return self.pack(values)

    def node_id(self, value) -> None:  # type: ignore[override] # noqa
        return None

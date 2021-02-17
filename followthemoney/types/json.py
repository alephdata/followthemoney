import json  # yay Python 3
from banal import ensure_list

from followthemoney.types.common import PropertyType
from followthemoney.util import sanitize_text, defer as _


class JsonType(PropertyType):
    """An encoded JSON object. This is used to store raw HTTP headers for documents
    and some other edge cases. It's a really bad idea and we should try to get rid
    of JSON properties."""

    name = "json"
    group = None
    label = _("Nested data")
    matchable = False

    def pack(self, obj):
        """Encode a given value to JSON."""
        # TODO: use a JSON encoder that handles more types?
        if obj is not None:
            return json.dumps(obj)

    def unpack(self, obj):
        """Decode a given JSON object."""
        if obj is None:
            return
        try:
            return json.loads(obj)
        except Exception:
            return obj

    def clean(self, obj, **kwargs):
        if not isinstance(obj, str):
            obj = self.pack(obj)
        else:
            obj = sanitize_text(obj)
        return obj

    def join(self, values):
        """Turn multiple values into a JSON array."""
        values = [self.unpack(v) for v in ensure_list(values)]
        return self.pack(values)

    def node_id(self, value):
        return None

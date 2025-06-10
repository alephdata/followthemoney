from typing import Optional, Dict, Any

from followthemoney.types import registry
from followthemoney.dataset.util import Named, cleanup
from followthemoney.dataset.util import type_check, type_require


class DataResource(Named):
    """A downloadable resource that is part of a dataset."""

    def __init__(self, data: Dict[str, Any]) -> None:
        name = type_require(registry.string, data.get("name", data.get("path")))
        super().__init__(name)
        self.url = type_require(registry.url, data.get("url"))
        self.checksum = type_check(registry.checksum, data.get("checksum"))
        self.timestamp = type_check(registry.date, data.get("timestamp"))
        self.mime_type = type_check(registry.mimetype, data.get("mime_type"))
        self.title = type_check(registry.string, data.get("title"))
        self.size = int(data["size"]) if "size" in data else None

    @property
    def mime_type_label(self) -> Optional[str]:
        if self.mime_type is None:
            return None
        return registry.mimetype.caption(self.mime_type)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "url": self.url,
            "checksum": self.checksum,
            "timestamp": self.timestamp,
            "mime_type": self.mime_type,
            "mime_type_label": self.mime_type_label,
            "title": self.title,
            "size": self.size,
        }
        return cleanup(data)

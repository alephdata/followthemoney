from banal import as_bool
from typing import Optional, Dict, Any

from followthemoney.types import registry
from followthemoney.dataset.util import Named, cleanup
from followthemoney.dataset.util import type_check, type_require


class DataPublisher(Named):
    """Publisher information, eg. the government authority."""

    def __init__(self, data: Dict[str, Any]):
        name = type_require(registry.string, data.get("name"))
        super().__init__(name)
        self.url = type_require(registry.url, data.get("url"))
        self.name_en = type_check(registry.string, data.get("name_en"))
        self.acronym = type_check(registry.string, data.get("acronym"))
        self.description = type_check(registry.string, data.get("description"))
        self.country = type_check(registry.country, data.get("country"))
        self.official = as_bool(data.get("official", False))
        self.logo_url = type_check(registry.url, data.get("logo_url"))

    @property
    def country_label(self) -> Optional[str]:
        if self.country is None:
            return None
        return registry.country.caption(self.country)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "name_en": self.name_en,
            "acronym": self.acronym,
            "url": self.url,
            "description": self.description,
            "country": self.country,
            "country_label": self.country_label,
            "official": self.official,
            "logo_url": self.logo_url,
        }
        return cleanup(data)

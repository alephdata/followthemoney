from typing import List, Any, Dict

from followthemoney.types import registry
from followthemoney.dataset.util import type_check, type_require, cleanup
from followthemoney.exc import MetadataException


class DataCoverage(object):
    """Details on the temporal and geographic scope of a dataset."""

    # Derived from Aleph
    FREQUENCIES = (
        "unknown",
        "never",
        "hourly",
        "daily",
        "weekly",
        "monthly",
        "annually",
    )

    def __init__(self, data: Dict[str, Any]) -> None:
        self.start = type_check(registry.date, data.get("start"))
        self.end = type_check(registry.date, data.get("end"))
        self.countries: List[str] = []
        for country in data.get("countries", []):
            self.countries.append(type_require(registry.country, country))
        self.frequency = type_check(
            registry.string, data.get("frequency", "unknown").lower()
        )
        if self.frequency not in self.FREQUENCIES:
            raise MetadataException(
                "Invalid coverage frequency: %r not in %s"
                % (self.frequency, self.FREQUENCIES)
            )
        self.schedule = type_check(registry.string, data.get("schedule"))

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "start": self.start,
            "end": self.end,
            "countries": self.countries,
            "frequency": self.frequency,
            "schedule": self.schedule,
        }
        return cleanup(data)

    def __repr__(self) -> str:
        return f"<DataCoverage({self.start!r}, {self.end!r}, {self.countries!r})>"

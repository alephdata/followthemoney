import io
import os
import logging
from banal.lists import ensure_list
import requests
from csv import DictReader
from urllib.parse import urlparse
from banal import keys_values, is_listish
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    ItemsView,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    cast,
)

from followthemoney.mapping.source import Record, Source
from followthemoney.util import sanitize_text
from followthemoney.exc import InvalidMapping

if TYPE_CHECKING:
    from followthemoney.mapping.query import QueryMapping

log = logging.getLogger(__name__)
FilterList = List[Tuple[str, Set[Optional[str]]]]


class CSVSource(Source):
    """Special case for entity loading directly from a CSV URL"""

    def __init__(self, query: "QueryMapping", data: Dict[str, Any]) -> None:
        super().__init__(query, data)
        self.urls: Set[str] = set()
        for url in keys_values(data, "csv_url", "csv_urls"):
            self.urls.add(cast(str, os.path.expandvars(url)))

        if not len(self.urls):
            raise InvalidMapping("No CSV URLs are specified.")

        self.filters_set = self._parse_filters(self.filters)
        self.filters_not_set = self._parse_filters(self.filters_not)

    def _parse_filters(self, filters: ItemsView[str, Any]) -> FilterList:
        filters_set: FilterList = []
        for (key, value) in filters:
            values = set(cast(List[Optional[str]], ensure_list(value)))
            filters_set.append((key, values))
        return filters_set

    def check_filters(self, data: Record) -> bool:
        for (k, v) in self.filters_set:
            if data.get(k) not in v:
                return False
        for (k, v) in self.filters_not_set:
            if data.get(k) in v:
                return False
        return True

    @classmethod
    def read_csv(cls, fh: Iterable[str]) -> Generator[Record, None, None]:
        for row in DictReader(fh, skipinitialspace=True):
            data: Record = {}
            for ref, ref_value in row.items():
                value = sanitize_text(ref_value)
                if value is not None:
                    data[ref] = value
            yield data

    def read_csv_url(self, url: str) -> Generator[Record, None, None]:
        parsed_url = urlparse(url)
        log.info("Loading: %s", url)
        if parsed_url.scheme in ["http", "https"]:
            res = requests.get(url, stream=True)
            if not res.ok:
                raise InvalidMapping("Failed to open CSV: %s" % url)
            # if res.encoding is None:
            res.encoding = "utf-8"
            # log.info("Detected encoding: %s", res.encoding)
            lines = res.iter_lines(decode_unicode=True)
            yield from self.read_csv(lines)
        else:
            with io.open(parsed_url.path, "r") as fh:
                yield from self.read_csv(fh)

    @property
    def records(self) -> Generator[Record, None, None]:
        """Iterate through the table applying filters on-the-go."""
        for url in self.urls:
            for record in self.read_csv_url(url):
                if self.check_filters(record):
                    yield record

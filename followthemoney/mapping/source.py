from typing import TYPE_CHECKING, Any, Dict, Generator, Optional, Set, cast

if TYPE_CHECKING:
    from followthemoney.mapping.query import QueryMapping

Filter = Set[Optional[str]]
Record = Dict[str, str]


class Source(object):
    def __init__(self, query: "QueryMapping", data: Dict[str, Any]) -> None:
        self.query = query
        self.filters = cast(Dict[str, Any], data.get("filters", {})).items()
        self.filters_not = cast(Dict[str, Any], data.get("filters_not", {})).items()

    @property
    def records(self) -> Generator[Record, None, None]:
        raise NotImplemented

    def __len__(self) -> int:
        return 0

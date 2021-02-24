from banal import ensure_list
from typing import Set, Dict, Type, Union, List, Optional

from followthemoney.types.common import PropertyType


class Registry(object):
    """This registry keeps the processing helpers for all property types
    in the system. They are instantiated as singletons when the system is first
    loaded. The registry can be used to get a type, which can itself then
    clean, validate or format values of that type."""

    def __init__(self) -> None:
        self.named: Dict[str, PropertyType] = {}
        self.matchable: Set[PropertyType] = set()
        self.types: Set[PropertyType] = set()
        self.groups: Dict[str, PropertyType] = {}
        self.pivots: Set[PropertyType] = set()

    def add(self, clazz: Type[PropertyType]) -> None:
        """Add a singleton class."""
        type_ = clazz()
        self.named[clazz.name] = type_
        self.types.add(type_)
        if type_.matchable:
            self.matchable.add(type_)
        if type_.pivot:
            self.pivots.add(type_)
        if type_.group is not None:
            self.groups[type_.group] = type_

    def get(self, name: Union[str, PropertyType]) -> Optional[PropertyType]:
        """For a given property type name, get its type object. This can also
        be used via getattr, e.g. ``registry.phone``."""
        # Allow transparent re-checking.
        if isinstance(name, PropertyType):
            return name
        return self.named.get(name)

    def get_types(self, names: List[Union[str, PropertyType]]) -> List[PropertyType]:
        """Get a list of all type names."""
        names = ensure_list(names)
        types = [self.get(n) for n in names]
        return [t for t in types if t is not None]

    def __getattr__(self, name: str) -> Optional[PropertyType]:
        return self.named[name]

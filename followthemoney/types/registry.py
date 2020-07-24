from banal import ensure_list
from followthemoney.types.common import PropertyType


class Registry(object):
    """This registry keeps the processing helpers for all property types
    in the system. It can be used to get a helper for a type, which can
    then clean, validate or format values of that type."""

    def __init__(self):
        self.named = {}
        self.matchable = set()
        self.types = set()
        self.groups = {}
        self.pivots = set()

    def add(self, clazz):
        if not issubclass(clazz, PropertyType):
            return
        type_ = clazz()
        self.named[clazz.name] = type_
        self.types.add(type_)
        if type_.matchable:
            self.matchable.add(type_)
        if type_.pivot:
            self.pivots.add(type_)
        if type_.group is not None:
            self.groups[type_.group] = type_

    def get(self, name):
        """For a given property type name, get its handling object."""
        # Allow transparent re-checking.
        if isinstance(name, PropertyType):
            return name
        return self.named.get(name)

    def get_types(self, names):
        names = ensure_list(names)
        return [self.get(n) for n in names if self.get(n) is not None]

    def __getattr__(self, name):
        return self.named[name]

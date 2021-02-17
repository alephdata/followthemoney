from banal import ensure_list
from followthemoney.types.common import PropertyType


class Registry(object):
    """This registry keeps the processing helpers for all property types
    in the system. They are instantiated as singletons when the system is first
    loaded. The registry can be used to get a type, which can itself then
    clean, validate or format values of that type."""

    def __init__(self):
        self.named = {}
        self.matchable = set()
        self.types = set()
        self.groups = {}
        self.pivots = set()

    def add(self, clazz):
        """Add a singleton class."""
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
        """For a given property type name, get its type object. This can also
        be used via getattr, e.g. ``registry.phone``."""
        # Allow transparent re-checking.
        if isinstance(name, PropertyType):
            return name
        return self.named.get(name)

    def get_types(self, names):
        """Get a list of all type names."""
        names = ensure_list(names)
        return [self.get(n) for n in names if self.get(n) is not None]

    def __getattr__(self, name):
        return self.named[name]

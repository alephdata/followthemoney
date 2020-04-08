from banal import ensure_list
from followthemoney.types.common import PropertyType


class Registry(object):
    """This registry keeps the processing helpers for all property types
    in the system. It can be used to get a helper for a type, which can
    then clean, validate or format values of that type."""

    def __init__(self):
        self._types = {}

    def add(self, clazz):
        if issubclass(clazz, PropertyType):
            self._types[clazz.name] = clazz()

    @property
    def types(self):
        """Return all types known to the system."""
        return list(self._types.values())

    @property
    def matchable(self):
        """Return all matchable property types."""
        return [t for t in self.types if t.matchable]

    @property
    def pivots(self):
        return [t for t in self.types if t.pivot]

    @property
    def groups(self):
        return {t.group: t for t in self.types if t.group is not None}

    def get(self, name):
        """For a given property type name, get its handling object."""
        # Allow transparent re-checking.
        if isinstance(name, PropertyType):
            return name
        return self._types.get(name)

    def get_types(self, names):
        names = ensure_list(names)
        return [self.get(n) for n in names if self.get(n) is not None]

    def __getattr__(self, name):
        type_ = self.get(name)
        if type_ is None:
            raise AttributeError(name)
        return type_

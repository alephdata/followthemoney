from pkg_resources import iter_entry_points

from followthemoney.types.common import PropertyType


class Registry(object):
    """This registry keeps the processing helpers for all property types
    in the system. It can be used to get a helper for a type, which can
    then clean, validate or format values of that type."""

    def __init__(self):
        self._types = {}
        self._all = set()

    def entry_points(self):
        yield from iter_entry_points('followthemoney.types')

    @property
    def types(self):
        """Return all types known to the system."""
        if not self._all:
            for ep in self.entry_points():
                self._all.add(self.get(ep.name))
        return self._all

    @property
    def matchable(self):
        """Return all matchable property types."""
        return [t for t in self.types if t.matchable]

    @property
    def groups(self):
        return {t.group: t for t in self.types if t.group is not None}

    def get(self, name):
        """For a given property type name, get its handling object."""
        # Allow transparent re-checking.
        if isinstance(name, PropertyType):
            return name
        if name not in self._types:
            for ep in self.entry_points():
                if ep.name == name:
                    clazz = ep.load()
                    if issubclass(clazz, PropertyType):
                        self._types[ep.name] = clazz()
        return self._types.get(name)

    def get_types(self, names):
        return [self.get(n) for n in names if self.get(n) is not None]

    def __getattr__(self, name):
        type_ = self.get(name)
        if type_ is None:
            raise AttributeError(name)
        return type_

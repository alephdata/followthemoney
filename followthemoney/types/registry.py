from pkg_resources import iter_entry_points


class Registry(object):

    def __init__(self):
        self._types = {}

    def entry_points(self):
        yield from iter_entry_points('followthemoney.types')

    @property
    def types(self):
        for ep in self.entry_points():
            yield self.get(ep.name)

    @property
    def groups(self):
        if not hasattr(self, '_groups'):
            self._groups = {}
            for type_ in self.types:
                self._groups[type_.group] = type_
        return self._groups

    def get(self, name):
        if name not in self._types:
            for ep in self.entry_points():
                if ep.name == name:
                    clazz = ep.load()
                    self._types[ep.name] = clazz()
        return self._types.get(name)

    def __getattr__(self, name):
        type_ = self.get(name)
        if type_ is None:
            raise AttributeError(name)
        return type_

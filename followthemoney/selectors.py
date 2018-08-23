

class PropertyType(object):

    def __init__(self, validator, name, tag, scheme):
        self.validator = validator
        self.name = name
        self.tag = tag
        self.scheme = scheme

    def validate(self, value):
        pass

    def normalize(self, value):
        pass

    def rdf(self, value):
        pass

    def key(self, value):
        pass


class Registry(object):

    def __init__(self):
        self._types = {}
        self._tags = {}

    def by_type(self, name):
        pass

    def by_tag(self, tag):
        pass

    def by_key(self, key):
        pass


class Statement(object):

    def __init__(subject, prop, object, weight=None):
        pass

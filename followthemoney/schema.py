from normality import stringify

from aleph.util import dict_list, ensure_list
from aleph.schema.types import resolve_type

from followthemoney.property import Property
from followthemoney.exc import InvalidData


class Schema(object):
    """Defines the abstract data model.

    Schema items define the entities and links available in the model.
    """

    ENTITY = 'entities'
    LINK = 'links'
    SECTIONS = [ENTITY, LINK]

    def __init__(self, schemata, section, name, data):
        assert section in self.SECTIONS, section
        self._schemata = schemata
        self.section = section
        self.name = name
        self.data = data
        self.label = data.get('label', name)
        self.plural = data.get('plural', self.label)
        self.icon = data.get('icon')
        # Do not show in listings:
        self.hidden = data.get('hidden', False)
        # Try to perform fuzzy matching. Fuzzy similarity search does not
        # make sense for entities which have a lot of similar names, such
        # as land plots, assets etc.
        self.fuzzy = data.get('fuzzy', True)
        self._extends = dict_list(data, 'extends')

        self._own_properties = []
        for name, prop in data.get('properties', {}).items():
            self._own_properties.append(Property(self, name, prop))

        self.forward = data.get('forward', self.label)
        self.reverse = data.get('reverse', self.label)

    @property
    def extends(self):
        """Return the inherited schemata."""
        for base in self._extends:
            yield self._schemata.get(base)

    @property
    def schemata(self):
        """Return the full inheritance chain."""
        yield self
        for base in self.extends:
            for schema in base.schemata:
                yield schema

    @property
    def properties(self):
        """Return properties, those defined locally and in ancestors."""
        names = set()
        for prop in self._own_properties:
            names.add(prop.name)
            yield prop
        for schema in self.extends:
            for prop in schema.properties:
                if prop.name in names:
                    continue
                names.add(prop.name)
                yield prop

    def get(self, name):
        for prop in self.properties:
            if prop.name == name:
                return prop
        raise ValueError("[%r] missing property: %s" % (self, name))

    def validate(self, data):
        """Validate a dataset against the given schema.

        This will also drop keys which are not present as properties.
        """
        result = {}
        errors = {}
        for prop in self.properties:
            value = data.get(prop.name)
            value, error = prop.validate(value)
            if error is not None:
                errors[prop.name] = error
            elif value is not None:
                result[prop.name] = value
        if len(errors):
            raise InvalidData(errors)
        return result

    def to_dict(self):
        data = {
            'type': self.section,
            'label': self.label,
            'plural': self.plural,
            'icon': self.icon,
            'hidden': self.hidden,
            'fuzzy': self.fuzzy,
            'properties': list(self.properties)
        }
        if self.section == Schema.LINK:
            data['forward'] = self.forward
            data['reverse'] = self.reverse
        return data

    def __repr__(self):
        return '<Schema(%r)>' % self.name

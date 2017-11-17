from banal import ensure_list

from followthemoney.property import Property
from followthemoney.exc import InvalidData, InvalidModel


class Schema(object):
    """Defines the abstract data model.

    Schema items define the entities and links available in the model.
    """

    def __init__(self, model, name, data):
        self._model = model
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
        self._extends = ensure_list(data.get('extends'))

        self._own_properties = []
        for name, prop in data.get('properties', {}).items():
            self._own_properties.append(Property(self, name, prop))

    @property
    def extends(self):
        """Return the inherited schemata."""
        for base in self._extends:
            basecls = self._model.get(base)
            if basecls is None:
                raise InvalidModel("No such schema: %s" % base)
            yield basecls

    @property
    def schemata(self):
        """Return the full inheritance chain."""
        yield self
        for base in self.extends:
            for schema in base.schemata:
                yield schema

    @property
    def names(self):
        return [s.name for s in self.schemata]

    @property
    def properties(self):
        """Return properties, those defined locally and in ancestors."""
        if not hasattr(self, '_properties'):
            properties = {}
            for schema in self.extends:
                for prop in schema.properties:
                    properties[prop.name] = prop
            for prop in self._own_properties:
                properties[prop.name] = prop
            self._properties = properties.values()
        return self._properties

    def get(self, name):
        for prop in self.properties:
            if prop.name == name:
                return prop

    def validate(self, data):
        """Validate a dataset against the given schema.

        This will also drop keys which are not present as properties.
        """
        result = {}
        errors = {}
        for prop in self.properties:
            if prop.name not in data:
                continue
            value = data.get(prop.name)
            value, error = prop.validate(value)
            if error is not None:
                errors[prop.name] = error
            elif value is not None:
                result[prop.name] = value
        if len(errors):
            raise InvalidData(errors)
        return result

    def invert(self, entity, cleaned=True):
        """Invert the properties of an entity into their normalised form."""
        properties = entity.get('properties', {})

        # Generate inverted representations of the data stored in properties.
        for prop in self.properties:
            values = properties.get(prop.name, [])
            if not len(values):
                continue

            # Find and set the name property
            if prop.is_label:
                entity['name'] = values[0]

            # Add inverted properties. This takes all the properties
            # of a specific type (names, dates, emails etc.)
            if prop.invert:
                if prop.invert not in entity:
                    entity[prop.invert] = []
                for norm in prop.type.normalize(values, cleaned=cleaned):
                    if norm not in entity[prop.invert]:
                        entity[prop.invert].append(norm)

        return entity

    def to_dict(self):
        data = {
            'label': self.label,
            'plural': self.plural,
            'icon': self.icon,
            'hidden': self.hidden,
            'fuzzy': self.fuzzy,
            'properties': [p.to_dict() for p in self.properties]
        }
        return data

    def __repr__(self):
        return '<Schema(%r)>' % self.name

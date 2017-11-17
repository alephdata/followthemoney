from banal import ensure_list

from followthemoney.exc import InvalidModel
from followthemoney.types import TYPES


class Property(object):

    def __init__(self, schema, name, data):
        self.schema = schema
        self.name = name.strip()
        self.data = data
        self.label = data.get('label', name)
        self.hidden = data.get('hidden', False)
        self.is_multiple = data.get('multiple', False)
        self.is_label = name == 'name'
        self.type_name = data.get('type', 'string')
        self.is_country = self.type_name == 'country'
        self.range = data.get('schema', 'Thing')
        try:
            self.type = TYPES[self.type_name].type
            self.invert = TYPES[self.type_name].invert
        except KeyError:
            raise InvalidModel("Invalid type: %s" % self.type_name)

    def validate(self, data):
        """Validate that the data should be stored.

        Since the types system doesn't really have validation, this currently
        tries to normalize the value to see if it passes strict parsing.
        """
        value, error = [], None
        for val in ensure_list(data):
            if not self.type.validate(val):
                error = "Invalid value"
            else:
                value.append(val)
        if not self.is_multiple:
            value = value[0] if len(value) else None
        else:
            value = list(set(value))
        if self.is_label and (value is None or not len(value)):
            error = "Field is required."
        return value, error

    def to_dict(self):
        return {
            'name': self.name,
            'label': self.label,
            'hidden': self.hidden,
            'type': self.type_name,
            'range': self.range
        }

    def __repr__(self):
        return '<Property(%r, %r)>' % (self.schema, self.name)

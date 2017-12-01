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
        self.required = data.get('required', False)
        self.is_multiple = data.get('multiple', False)
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
        values, error = [], None
        for val in ensure_list(data):
            if not self.type.validate(val):
                error = "Invalid value"
            else:
                values.append(val)
        if self.required and not len(values):
            error = 'Required'
        if error is not None:
            return ensure_list(data), error
        values = list(set(values))
        return values, None

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

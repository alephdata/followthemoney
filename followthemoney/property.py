from banal import ensure_list

from followthemoney.exc import InvalidModel
from followthemoney.types import TYPES
from followthemoney.util import gettext


class Property(object):

    def __init__(self, schema, name, data):
        self.schema = schema
        self.name = name.strip()
        self.qname = '%s:%s' % (schema.name, self.name)
        self.data = data
        self.label = data.get('label', name)
        self.description = data.get('description')
        self.caption = data.get('caption', False)
        self.required = data.get('required', False)
        self.is_multiple = data.get('multiple', False)
        self.type_name = data.get('type', 'string')
        self.range = data.get('schema', 'Thing')
        self.reverse = data.get('reverse')
        self.is_country = self.type_name == 'country'
        self.is_entity = self.type_name == 'entity'
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
            if isinstance(val, dict):
                val = val.get('id')
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

    def __eq__(self, other):
        return self.qname == other.qname

    def __hash__(self):
        return hash(self.qname)

    def to_dict(self):
        data = {
            'name': self.name,
            'qname': self.qname,
            'label': gettext(self.label),
            'description': gettext(self.description),
            'caption': self.caption,
            'type': self.type_name
        }
        if self.is_entity:
            data['range'] = self.range
            data['reverse'] = self.reverse
        return data

    def __repr__(self):
        return '<Property(%r, %r)>' % (self.schema, self.name)

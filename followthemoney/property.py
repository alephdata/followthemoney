from banal import ensure_list
from rdflib import URIRef

from followthemoney.exc import InvalidModel
from followthemoney.types import registry
from followthemoney.util import gettext, NAMESPACE


class Property(object):

    def __init__(self, schema, name, data):
        self.schema = schema
        self.name = name.strip()
        self.qname = '%s:%s' % (schema.name, self.name)
        self.data = data
        self._label = data.get('label', name)
        self._description = data.get('description')
        self.caption = data.get('caption', False)
        self.required = data.get('required', False)
        self._type = data.get('type', 'text')
        self.type = registry.get(self._type)
        if self.type is None:
            raise InvalidModel("Invalid type: %s" % self._type)

        self.range = data.get('schema', 'Thing')
        self._reverse = data.get('reverse')
        self.stub = data.get('stub', False)

        self.uri = NAMESPACE[self.qname]
        if 'rdf' in data:
            self.uri = URIRef(data.get('rdf'))

    @property
    def label(self):
        return gettext(self._label)

    @property
    def reverse(self):
        if self._reverse is not None:
            return gettext(self._reverse)

    @property
    def description(self):
        return gettext(self._description)

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
            'label': self.label,
            'description': self.description,
            'caption': self.caption,
            'uri': str(self.rdf),
            'type': self.type_name
        }
        if self.type == registry.entity:
            data['stub'] = self.stub
            data['range'] = self.range
            data['reverse'] = self.reverse
        return data

    def __repr__(self):
        return '<Property(%r, %r)>' % (self.schema, self.name)

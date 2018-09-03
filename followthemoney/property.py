from banal import ensure_list, is_mapping
from rdflib import URIRef

from followthemoney.exc import InvalidModel
from followthemoney.types import registry
from followthemoney.util import gettext, NAMESPACE


class Property(object):

    def __init__(self, schema, name, data, stub=False):
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

        self.range = None
        self.reverse = None
        self.stub = stub

        self.uri = NAMESPACE[self.qname]
        if 'rdf' in data:
            self.uri = URIRef(data.get('rdf'))

    def generate(self):
        range_ = self.data.get('schema', 'Thing')
        if range_:
            self.range = self.schema.model.get(range_)
            if self.range is None:
                raise InvalidModel("Cannot find range: %s" % self._range)

        reverse_ = self.data.get('reverse')
        if self.range and reverse_:
            if not is_mapping(reverse_):
                raise InvalidModel("Invalid reverse: %s" % self)
            self.reverse = self.range._add_reverse(reverse_, self)

    @property
    def label(self):
        return gettext(self._label)

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
                error = gettext('Invalid value')
            else:
                values.append(val)
        if self.required and not len(values):
            error = gettext('Required')
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
            'uri': str(self.uri),
            'type': self._type
        }
        if self.type == registry.entity:
            data['stub'] = self.stub
        if self.range:
            data['schema'] = self.range.name
        if self.reverse:
            data['reverse'] = self.reverse.name
        return data

    def __repr__(self):
        return '<Property(%r, %r)>' % (self.schema, self.name)

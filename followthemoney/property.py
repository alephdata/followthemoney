from normality import stringify
from banal import is_mapping
from rdflib import URIRef

from followthemoney.exc import InvalidModel
from followthemoney.types import registry
from followthemoney.util import gettext, NS, get_entity_id


class Property(object):
    RESERVED = ['id', 'caption', 'schema', 'schemata']

    def __init__(self, schema, name, data):
        self.schema = schema
        self.model = schema.model

        self.name = stringify(name)
        self.qname = '%s:%s' % (schema.name, self.name)
        if self.name in self.RESERVED:
            raise InvalidModel("Reserved name: %s" % self.name)

        self.data = data
        self._label = data.get('label', name)
        self._description = data.get('description')
        self.hidden = data.get('hidden', False)
        self.stub = data.get('stub', False)

        type_ = data.get('type', 'string')
        self.type = registry.get(type_)
        if self.type is None:
            raise InvalidModel("Invalid type: %s" % type_)

        self.matchable = data.get('matchable', self.type.matchable)
        self.range = None
        self.reverse = None
        self.uri = URIRef(data.get('rdf', NS[self.qname]))

    def generate(self):
        self.model.properties.add(self)

        if self.range is None and self.type == registry.entity:
            self.range = self.model.get(self.data.get('range'))

        reverse_ = self.data.get('reverse')
        if self.reverse is None and self.range and reverse_:
            if not is_mapping(reverse_):
                raise InvalidModel("Invalid reverse: %s" % self)
            self.reverse = self.range._add_reverse(reverse_, self)

    @property
    def label(self):
        return gettext(self._label)

    @property
    def description(self):
        return gettext(self._description)

    def specificity(self, value):
        """Return a measure of how precise the given value is."""
        if not self.matchable:
            return 0
        return self.type.specificity(value)

    def validate(self, data):
        """Validate that the data should be stored.

        Since the types system doesn't really have validation, this currently
        tries to normalize the value to see if it passes strict parsing.
        """
        values = []
        for val in data:
            if self.stub:
                return gettext('Property cannot be written')
            val = get_entity_id(val)
            if not self.type.validate(val):
                return gettext('Invalid value')
            if val is not None:
                values.append(val)

    def __eq__(self, other):
        return self.qname == other.qname

    def __hash__(self):
        return hash(self.qname)

    def to_dict(self):
        data = {
            'name': self.name,
            'qname': self.qname,
            'label': self.label,
            'type': self.type.name,
        }
        if self.description:
            data['description'] = self.description
        if self.stub:
            data['stub'] = True
        if self.matchable:
            data['matchable'] = True
        if self.hidden:
            data['hidden'] = True
        if self.range:
            data['range'] = self.range.name
        if self.reverse:
            data['reverse'] = self.reverse.name
        return data

    def __repr__(self):
        return '<Property(%r)>' % self.qname

    def __str__(self):
        return self.qname

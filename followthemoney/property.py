from normality import stringify
from banal import ensure_list, is_mapping
from rdflib import URIRef

from followthemoney.exc import InvalidModel
from followthemoney.types import registry
from followthemoney.util import gettext, NS


class Property(object):

    def __init__(self, schema, name, data):
        self.schema = schema
        self.model = schema.model
        self.name = stringify(name)
        self.qname = '%s:%s' % (schema.name, self.name)
        self.data = data
        self._label = data.get('label', name)
        self._description = data.get('description')
        self.caption = data.get('caption', False)
        self.required = data.get('required', False)
        self.stub = data.get('stub', False)

        type_ = data.get('type', 'string')
        self.type = registry.get(type_)
        if self.type is None:
            raise InvalidModel("Invalid type: %s" % type_)

        self.range = None
        self.reverse = None
        self.uri = URIRef(data.get('rdf', NS[self.qname]))

    def generate(self):
        self.model.properties.add(self)

        if self.range is None and self.type == registry.entity:
            self.range = self.model.get(self.data.get('schema'))

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

    def validate(self, data):
        """Validate that the data should be stored.

        Since the types system doesn't really have validation, this currently
        tries to normalize the value to see if it passes strict parsing.
        """
        values = []
        for val in ensure_list(data):
            if is_mapping(val):
                val = val.get('id')
            if not self.type.validate(val):
                return gettext('Invalid value')
            if val is not None:
                values.append(val)
        if self.required and not len(values):
            return gettext('Required')

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
            'stub': self.stub,
            'uri': str(self.uri),
            'type': self.type.name
        }
        if self.range:
            data['schema'] = self.range.name
        if self.reverse:
            data['reverse'] = self.reverse.name
        return data

    def __repr__(self):
        return '<Property(%r)>' % self.qname

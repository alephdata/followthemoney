from normality import stringify  # type: ignore
from banal import is_mapping
from rdflib import URIRef  # type: ignore
from typing import Dict, Any, Mapping, Optional, TYPE_CHECKING

from followthemoney.exc import InvalidModel
from followthemoney.types.common import PropertyType
from followthemoney.types import registry
from followthemoney.util import gettext, NS, get_entity_id

if TYPE_CHECKING:
    from followthemoney.schema import Schema
    from followthemoney.model import Model


class Property(object):
    RESERVED = ['id', 'caption', 'schema', 'schemata']

    def __init__(self, schema: 'Schema', name: str, data: Mapping[str, Any]):
        self.schema: 'Schema' = schema
        self.model: 'Model' = schema.model

        self.name: str = stringify(name)
        self.qname: str = '%s:%s' % (schema.name, self.name)
        if self.name in self.RESERVED:
            raise InvalidModel("Reserved name: %s" % self.name)

        self.data = data
        self._label: str = data.get('label', name)
        self._description: Optional[str] = data.get('description')
        self.hidden: bool = data.get('hidden', False)
        self.stub: bool = data.get('stub', False)

        self.type: PropertyType = registry.get(data.get('type', 'string'))
        self.matchable: bool = data.get('matchable', self.type.matchable)
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

    def to_dict(self) -> Dict[str, Any]:
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

from followthemoney.mapping.entity import EntityMapping
from followthemoney.exc import InvalidMapping


class QueryMapping(object):

    def __init__(self, model, data, key_prefix=None):
        self.model = model
        self.data = data

        self.mappings = {}
        self.refs = set()
        for name, data in data.get('entities', {}).items():
            mapping = EntityMapping(
                self, model, name, data, key_prefix=key_prefix)
            self.mappings[name] = mapping
            self.refs.update(mapping.refs)

        if not len(self.mappings):
            raise InvalidMapping("No entity mappings defined.")

    def map(self, record):
        entities = {}
        for name, mapping in self.mappings.items():
            entity = mapping.map(record)
            entities[name] = entity

        for name, entity in entities.items():
            mapping = self.mappings.get(name)
            mapping.resolve(entity, entities)
        return entities

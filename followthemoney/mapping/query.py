from followthemoney.mapping.entity import EntityMapping
from followthemoney.exc import InvalidMapping


class QueryMapping(object):

    def __init__(self, model, data, key_prefix=None):
        self.model = model
        self.data = data

        self.refs = set()
        self.entities = []
        for name, data in data.get('entities', {}).items():
            entity = EntityMapping(model, self, name, data,
                                   key_prefix=key_prefix)

            self.entities.append(entity)
            self.refs.update(entity.refs)

        if not len(self.entities):
            raise InvalidMapping("No entity mappings are defined.")

        # Check if the provided links satisfy the ranges of the given
        # properties (e.g. the owner of a company must be a legal person)
        for entity in self.entities:
            entity.bind()

        # Do dependency resolution, i.e. find the right order to
        # map these entities. This is needed to resolve entity IDs
        # in dependent entities.
        entities = self.entities
        self.entities = []
        resolved = set()
        while len(entities) > 0:
            before = len(entities)
            for entity in entities:
                if entity.dependencies.issubset(resolved):
                    self.entities.append(entity)
                    entities.remove(entity)
                    resolved.add(entity.name)
                    break
            if before == len(entities):
                raise InvalidMapping("Circular entity dependency detected.")

    def map(self, record):
        data = {}
        for entity in self.entities:
            mapped = entity.map(record, data)
            if mapped is not None:
                data[entity.name] = mapped
        return data

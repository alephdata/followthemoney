from followthemoney.types import registry


class Exporter(object):

    def exportable_properties(self, schema):
        for prop in schema.sorted_properties:
            if prop.hidden or prop.type == registry.entity:
                continue
            yield prop

    def exportable_fields(self, proxy):
        for prop in self.exportable_properties(proxy.schema):
            yield prop, proxy.get(prop)

    def write(self, proxy, **kwargs):
        pass

    def finalize(self):
        pass

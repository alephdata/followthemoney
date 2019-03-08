import csv


def write_entity(fh, entity, extra_fields=None):
    if extra_fields is None:
        extra_fields = dict()
    fieldnames = [prop.label for prop in entity.schema.sorted_properties]
    fieldnames = ['id'] + list(extra_fields.keys()) + fieldnames
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    prop_dict = {
        'id': entity.id,
        **extra_fields
    }
    for prop in entity.schema.sorted_properties:
        prop_dict[prop.label] = prop.type.join(entity.get(prop))
    writer.writerow(prop_dict)


def write_headers(fh, schema, extra_headers=None):
    if extra_headers is None:
        extra_headers = []
    fieldnames = [prop.label for prop in schema.sorted_properties]
    fieldnames = ['id'] + extra_headers + fieldnames
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    writer.writeheader()

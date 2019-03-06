import csv


def write_entity(fh, entity):
    fieldnames = [prop.label for prop in entity.schema.sorted_properties]
    fieldnames = ['id', ] + fieldnames
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    prop_dict = {'id': entity.id}
    for prop in entity.schema.sorted_properties:
        prop_dict[prop.label] = prop.type.join(entity.get(prop))
    writer.writerow(prop_dict)


def write_headers(fh, schema):
    fieldnames = [prop.label for prop in schema.sorted_properties]
    fieldnames = ['id', ] + fieldnames
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    writer.writeheader()

from followthemoney import model


for schema in model:
    if not schema.abstract:
        label = schema.description or schema.label
        print('%s [%s]' % (schema.name, label.strip()))
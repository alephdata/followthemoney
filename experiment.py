import sys
import yaml

from followthemoney import model


def execute_mapping(query):
    for entity in model.map_entities(query):
        schema = model.get(entity['schema'])
        print(entity)


if __name__ == '__main__':
    mapping_file = sys.argv[1]
    with open(mapping_file, 'r') as fh:
        data = yaml.load(fh)
        for dataset, mapping in data.items():
            for query in mapping.get('queries'):
                execute_mapping(query)

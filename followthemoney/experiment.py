import os
import sys
import yaml

from followthemoney.model import Model

model_path = os.path.dirname(__file__)
model_path = os.path.join(model_path, 'schema')
model = Model(model_path)


def execute_mapping(query):
    for entity in model.map_entities(query):
        print(entity)


if __name__ == '__main__':
    mapping_file = sys.argv[1]
    with open(mapping_file, 'r') as fh:
        data = yaml.load(fh)
        for dataset, mapping in data.items():
            for query in mapping.get('queries'):
                execute_mapping(query)

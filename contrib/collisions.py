from collections import defaultdict
from followthemoney import model

by_name = defaultdict(set)
for schema in model:
    for prop in schema.properties.values():
        by_name[prop.name].add(prop)

for props in by_name.values():
    if len(props) == 1:
        continue

    types = set([p.type for p in props])
    if len(types) > 1:
        print(f"[{props}] divergent types: {types}")
    
    labels = set([p.label for p in props])
    if len(labels) > 1:
        print(f"[{props}] divergent labels: {labels}")

    # print(props)
import sys
from collections import defaultdict
from followthemoney import model


IGNORE_DIVERGENT_TYPES = [
    "author",
    "organization",
    "gender",
    "number",
    "authority",
    "duration",
    "cpvCode",
    "nutsCode",
    "area",
    "subject",
    "sender",
]

IGNORE_DIVERGENT_LABELS = [
    "wikidataId",
    "parent",
    "holder",
    "number",
    "authority",
    "title",
    "cpvCode",
    "nutsCode",
    "criteria",
    "procedure",
    "callForTenders",
    "ticker",
]

IGNORE_LABEL_COLLISIONS = [
    "Address",
    "Notes",
    "Customs declarations",
    "Country of origin",
    "Payments received",
    "Payments made",
    "Entity",
    "The language of the translated text",
    "Responding to",
    "ISIN",
    "Document number",
]


def test_divergent_types(by_name):
    divergent = {}

    for name, props in by_name.items():
        if len(props) == 1 or name in IGNORE_DIVERGENT_TYPES:
            continue

        types = set([p.type for p in props])
        if len(types) > 1:
            divergent[name] = props

    return divergent


def test_divergent_labels(by_name):
    divergent = {}

    for name, props in by_name.items():
        if len(props) == 1 or name in IGNORE_DIVERGENT_LABELS:
            continue
        
        labels = set([p.label for p in props])
        if len(labels) > 1:
            divergent[name] = props

    return divergent


def test_label_collisions(by_label):
    collisions = {}

    for label, props in by_label.items():
        if len(props) == 1 or label in IGNORE_LABEL_COLLISIONS:
            continue

        names = set([p.name for p in props])
        if len(names) > 1:
            collisions[label] = props

    return collisions


if __name__ == '__main__':
    by_name = defaultdict(set)
    by_label = defaultdict(set)

    for schema in model:
        for prop in schema.properties.values():
            by_name[prop.name].add(prop)
            by_label[prop.label].add(prop)

    divergent_types = test_divergent_types(by_name)
    divergent_labels = test_divergent_labels(by_name)
    label_collisions = test_label_collisions(by_label)

    failed = False

    if divergent_types:
        failed = True
        print("DIVERGENT TYPES\n")
        for name, props in divergent_types.items():
            print(f"  {name}:")
            for prop in props:
                print(f"  * {prop.qname} - {prop.type.name}")
            print()
        print()

    if divergent_labels:
        failed = True
        print("DIVERGENT LABELS\n")
        for name, props in divergent_labels.items():
            print(f"  {name}:")
            for prop in props:
                print(f"  * {prop.qname} - {prop.label}")
            print()
        print()

    if label_collisions:
        failed = True
        print("COLLIDING LABELS\n")
        for label, props in label_collisions.items():
            print(f"  {label}:")
            for prop in props:
                print(f"  * {prop.qname}")
            print()

    if failed:
        sys.exit(1)

    print("No issues found.")

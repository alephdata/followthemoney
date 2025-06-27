import sys
from collections import defaultdict
from followthemoney import model


IGNORE_DIVERGENT_TYPES = [
    "number",
    "authority",
    "area",
    "subject",
    "sender",
]

IGNORE_DIVERGENT_LABELS = [
    "parent",
    "holder",
    "number",
    "authority",
    "criteria",
    "procedure",
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

IGNORE_LABEL_CAPITALIZATION = [
    "ibcRUC",
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


def test_label_capitalization():
    issues = []

    for schema in model:
        for prop in schema.properties.values():
            if (
                not prop.label[0].isupper()
                and prop.label not in IGNORE_LABEL_CAPITALIZATION
            ):
                issues.append(prop)

    return issues


if __name__ == "__main__":
    by_name = defaultdict(set)
    by_label = defaultdict(set)

    for schema in model:
        for prop in schema.properties.values():
            by_name[prop.name].add(prop)
            by_label[prop.label].add(prop)

    divergent_types = test_divergent_types(by_name)
    divergent_labels = test_divergent_labels(by_name)
    label_collisions = test_label_collisions(by_label)
    label_issues = test_label_capitalization()

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

    if label_issues:
        failed = True
        print("WRONG PROPERTY LABEL CAPITALIZATION\n")
        for prop in label_issues:
            print(f"  {prop.qname} - {prop.label}")

    if failed:
        sys.exit(1)

    print("No issues found.")

import itertools
from fuzzywuzzy import fuzz
from normality import normalize
import fingerprints
from followthemoney.types import registry

# OK, Here's the plan: we have to find a way to get user judgements
# on as many of these matches as we can, then build a regression
# model which properly weights the value of a matching property
# based upon it's type.
NAMES_WEIGHT = 0.6
COUNTRIES_WEIGHT = 0.1
MATCH_WEIGHTS = {
    registry.text: 0,
    registry.name: 0,  # because we already compare names
    registry.identifier: 0.3,
    registry.url: 0.1,
    registry.email: 0.2,
    registry.ip: 0.1,
    registry.iban: 0.3,
    registry.address: 0.3,
    registry.date: 0.2,
    registry.phone: 0.3,
    registry.country: 0.1,
}


def compare(model, left, right):
    """Compare two entities and return a match score."""
    left = model.get_proxy(left)
    right = model.get_proxy(right)
    if right.schema not in list(left.schema.matchable_schemata):
        return 0
    schema = model.common_schema(left.schema, right.schema)
    score = 0
    weight_sum = 0
    try:
        score += compare_names(left, right) * NAMES_WEIGHT
        weight_sum += NAMES_WEIGHT
    except ValueError:
        pass
    try:
        score += compare_countries(left, right) * COUNTRIES_WEIGHT
        weight_sum += COUNTRIES_WEIGHT
    except ValueError:
        pass
    for name, prop in schema.properties.items():
        weight = MATCH_WEIGHTS.get(prop.type, 0)
        if weight == 0 or not prop.matchable:
            continue

        left_values = left.get(name, quiet=True)
        right_values = right.get(name, quiet=True)
        if left_values or right_values:
            weight_sum += weight
        if not left_values or not right:
            continue
        prop_score = prop.type.compare_sets(left_values, right_values)
        score += prop_score * weight
    if not weight_sum:
        return 0
    return score / weight_sum


def _normalize_names(names):
    """Generate a sequence of comparable names for an entity. This also
    generates a `fingerprint`, i.e. a version of the name where all tokens
    are sorted alphabetically, and some parts, such as company suffixes,
    have been removed."""
    seen = set()
    for name in names:
        plain = normalize(name, ascii=True)
        if plain is not None and plain not in seen:
            seen.add(plain)
            yield plain
        fp = fingerprints.generate(name)
        if fp is not None and len(fp) > 6 and fp not in seen:
            seen.add(fp)
            yield fp


def compare_names(left, right):
    result = 0
    left_list = list(_normalize_names(left.names))
    right_list = list(_normalize_names(right.names))
    if not (left_list or right_list):
        raise ValueError
    for (left, right) in itertools.product(left_list, right_list):
        if not (left or right):
            continue
        similarity = fuzz.WRatio(left, right, full_process=False)
        result = max(result, similarity)
    return result


def compare_countries(left, right):
    left = left.country_hints
    right = right.country_hints
    if not (left or right):
        raise ValueError
    intersection = left.intersection(right)
    union = left.union(right)
    return len(intersection) / len(union)

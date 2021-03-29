import itertools
from collections import defaultdict

from fuzzywuzzy import fuzz
from normality import normalize
import fingerprints
from followthemoney.types import registry

# OK, Here's the plan: we have to find a way to get user judgements
# on as many of these matches as we can, then build a regression
# model which properly weights the value of a matching property
# based upon it's type.
MATCH_WEIGHTS = {
    registry.name: 0.6,
    registry.country: 0.1,
    registry.identifier: 0.3,
    registry.url: 0.1,
    registry.email: 0.2,
    registry.ip: 0.1,
    registry.iban: 0.3,
    registry.address: 0.3,
    registry.date: 0.2,
    registry.phone: 0.3,
}


def compare_scores(model, left, right):
    """Compare two entities and return a match score for each property."""
    left = model.get_proxy(left)
    right = model.get_proxy(right)
    if right.schema not in list(left.schema.matchable_schemata):
        return {}
    schema = model.common_schema(left.schema, right.schema)
    scores = defaultdict(list)
    for name, prop in schema.properties.items():
        if not prop.matchable:
            continue
        try:
            score = compare_prop(prop, left, right)
            scores[prop.type].append(score)
        except ValueError:
            pass
    return scores


def compare(model, left, right):
    """Compare two entities and return a match score."""
    scores = compare_scores(model, left, right)
    weighted_score = 0
    weights_sum = 0
    for prop, score in scores.items():
        weight = MATCH_WEIGHTS.get(prop, 0)
        weighted_score += max(score) * weight
        weights_sum += weight
    if not weights_sum:
        return 0.0
    return weighted_score / weights_sum


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


def compare_prop(prop, left, right):
    if prop.type == registry.name:
        return compare_names(left, right)
    elif prop.type == registry.country:
        return compare_countries(left, right)
    left_values = left.get(prop.name, quiet=True)
    right_values = right.get(prop.name, quiet=True)
    if not left_values and not right_values:
        raise ValueError("At least one proxy must have property: %s", prop)
    elif not left_values or not right_values:
        return 0.0
    return prop.type.compare_sets(left_values, right_values)


def compare_names(left, right):
    result = 0.0
    left_list = list(_normalize_names(left.names))
    right_list = list(_normalize_names(right.names))
    if not left_list and not right_list:
        raise ValueError("At least one proxy must have name properties")
    elif not left_list or not right_list:
        return 0.0
    for (left, right) in itertools.product(left_list, right_list):
        similarity = fuzz.WRatio(left, right, full_process=False) / 100.0
        result = max(result, similarity)
    return result


def compare_countries(left, right):
    left_countries = left.country_hints
    right_countries = right.country_hints
    if not left_countries and not right_countries:
        raise ValueError("At least one proxy must have country properties")
    elif not left_countries or not right_countries:
        return 0.0
    intersection = left_countries.intersection(right_countries)
    union = left_countries.union(right_countries)
    return len(intersection) / len(union)

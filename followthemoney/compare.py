import itertools
from banal import ensure_list
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
MISSING_WEIGHT = 0.75


def compare_scores(
    model, left, right, include_prop_types=None, exclude_prop_types=None
):
    """Compare two entities and return a match score for each property."""
    left = model.get_proxy(left)
    right = model.get_proxy(right)
    if right.schema not in list(left.schema.matchable_schemata):
        return {}
    # schema = model.common_schema(left.schema, right.schema)
    scores = defaultdict(list)
    # try:
    #     scores[registry.name] = [compare_names(left, right)]
    # except ValueError:
    #     pass
    # try:
    #     scores[registry.country] = [compare_countries(left, right)]
    # except ValueError:
    #     pass
    prop_types = include_prop_types or scores.keys()
    for exclude in ensure_list(exclude_prop_types):
        prop_types.discard(exclude)
    for prop_type in prop_types:
        try:
            scores[prop_type] = compare_type(prop_type, left, right)
        except ValueError:
            pass
    return scores

    # exclude_prop_types = set(exclude_prop_types or []).union(scores.keys())
    # for name, prop in schema.properties.items():
    #     if not prop.matchable:
    #         continue
    #     elif include_prop_types and prop.type not in include_prop_types:
    #         continue
    #     elif exclude_prop_types and prop.type in exclude_prop_types:
    #         continue
    #     try:
    #         score = compare_prop(prop, left, right)
    #         scores[prop.type].append(score)
    #     except ValueError:
    #         pass
    # return scores


def compare(model, left, right):
    """Compare two entities and return a match score."""
    scores = compare_scores(model, left, right, set(MATCH_WEIGHTS.keys()))
    weighted_score = 0
    weights_sum = 0
    for prop_type, score in scores.items():
        weight = MATCH_WEIGHTS.get(prop_type, 0)
        try:
            weighted_score += score * weight
            weights_sum += weight
        except ValueError:
            weights_sum += weight * MISSING_WEIGHT
    if not weights_sum:
        return 0.0
    return weighted_score / weights_sum


def compare_type(prop_type, left, right):
    if prop_type == registry.country:
        return compare_countries(left, right)
    left_values = left.get_type_values(prop_type, matchable=True)
    right_values = right.get_type_values(prop_type, matchable=True)
    if prop_type == registry.name:
        return compare_names(left_values, right_values)
    if not len(left_values) and not len(right_values):
        raise ValueError("At least one proxy must have type: %s", prop_type)
    elif not left_values or not right_values:
        return None
    return prop_type.compare_sets(left_values, right_values)


# def compare_prop(prop, left, right):
#     left_values = left.get(prop.name, quiet=True)
#     right_values = right.get(prop.name, quiet=True)
#     if not left_values and not right_values:
#         raise ValueError("At least one proxy must have property: %s", prop)
#     elif not left_values or not right_values:
#         return None
#     return prop.type.compare_sets(left_values, right_values)


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


def compare_names(left_names, right_names, max_names=200):
    result = 0.0
    left_list = list(itertools.islice(_normalize_names(left_names), max_names))
    right_list = list(itertools.islice(_normalize_names(right_names), max_names))
    if not left_list and not right_list:
        raise ValueError("At least one proxy must have name properties")
    elif not left_list or not right_list:
        return None
    for (left, right) in itertools.product(left_list, right_list):
        similarity = fuzz.WRatio(left, right, full_process=False) / 100.0
        result = max(result, similarity)
        if result == 1.0:
            break
    result *= min(
        1.0, 2 ** (-len(left_list) * len(right_list) / (max_names * max_names))
    )
    return result


def compare_countries(left, right):
    left_countries = left.country_hints
    right_countries = right.country_hints
    if not left_countries and not right_countries:
        raise ValueError("At least one proxy must have country properties")
    elif not left_countries or not right_countries:
        return None
    intersection = left_countries.intersection(right_countries)
    union = left_countries.union(right_countries)
    return len(intersection) / len(union)

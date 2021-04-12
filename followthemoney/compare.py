import itertools
import math
import warnings

from fuzzywuzzy import fuzz
from normality import normalize
import fingerprints
from followthemoney.exc import InvalidData
from followthemoney.types import registry


# Compare weights come from the glm-bernouli model in followthemoney-predict
COMPARE_WEIGHTS = {
    registry.name: 12.275729155073371,
    registry.country: 1.0494517476987815,
    registry.date: 6.960245940274218,
    registry.identifier: 5.2209896558064175,
    registry.address: 6.456137299747168,
    registry.phone: 3.538892687331418,
    registry.email: 14.115925628770384,
    registry.iban: 0.019140301711998726,
    registry.url: 3.211995327345834,
    None: -11.91521189545115,
}


class FTMPredictWarning(UserWarning):
    def __str__(self):
        return (
            "followthemoney.compare uses a simplified model. Use the package "
            "followthemoney-predict for a more accurate entity comparison model"
        )


warnings.simplefilter("once", FTMPredictWarning)


def compare_scores(model, left, right):
    """Compare two entities and return a match score for each property."""
    left = model.get_proxy(left)
    right = model.get_proxy(right)
    try:
        model.common_schema(left.schema, right.schema)
    except InvalidData:
        return {}
    scores = dict()
    left_inv = left.get_type_inverted(matchable=True)
    right_inv = right.get_type_inverted(matchable=True)
    left_groups = set(left_inv.keys())
    right_groups = set(right_inv.keys())
    for group_name in left_groups.intersection(right_groups):
        group = registry.groups[group_name]
        try:
            if group == registry.name:
                score = compare_names(left, right)
            elif group == registry.country:
                score = compare_countries(left, right)
            else:
                score = compare_group(
                    group, left_inv[group_name], right_inv[group_name]
                )
            scores[group] = score
        except ValueError:
            pass
    for group_name in left_groups.symmetric_difference(right_groups):
        group = registry.groups[group_name]
        scores[group] = None
    return scores


def _compare(scores, weights, n_std=1):
    warnings.warn(FTMPredictWarning())
    if not scores or not any(scores.values()):
        return 0.0
    prob = 0
    for field, weight in weights.items():
        if field:
            prob += weight * (scores.get(field) or 0.0)
        else:
            prob += weight
    return 1.0 / (1.0 + math.exp(-prob))


def compare(model, left, right, weights=COMPARE_WEIGHTS):
    """Compare two entities and return a match score."""
    scores = compare_scores(model, left, right)
    return _compare(scores, weights)


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


def compare_group(group_type, left_values, right_values):
    if not left_values and not right_values:
        raise ValueError("At least one proxy must have property type: %s", group_type)
    elif not left_values or not right_values:
        return None
    return group_type.compare_sets(left_values, right_values)


def compare_names(left, right, max_names=200):
    result = 0.0
    left_list = list(itertools.islice(_normalize_names(left.names), max_names))
    right_list = list(itertools.islice(_normalize_names(right.names), max_names))
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

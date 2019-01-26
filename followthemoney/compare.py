import itertools
from Levenshtein import jaro
from normality import normalize
from followthemoney.types import registry
from followthemoney.util import dampen, shortest
from followthemoney.exc import InvalidData

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
    """Compare two entities and return number between 0 and 1.
    Returned number indicates probability that two entities are the same.
    """
    left = model.get_proxy(left)
    right = model.get_proxy(right)
    if right.schema not in list(left.schema.matchable_schemata):
        return 0
    schema = model.common_schema(left.schema, right.schema)
    score = compare_names(left, right) * NAMES_WEIGHT
    score += compare_countries(left, right) * COUNTRIES_WEIGHT
    for name, prop in schema.properties.items():
        weight = MATCH_WEIGHTS.get(prop.type, 0)
        if weight == 0 or not prop.matchable:
            continue
        try:
            left_values = left.get(name)
            right_values = right.get(name)
        except InvalidData:
            continue

        if not len(left_values) or not len(right_values):
            continue
        prop_score = prop.type.compare_sets(left_values, right_values)
        score += (prop_score * weight)
    return score


def compare_names(left, right):
    result = 0
    left_list = [normalize(n, latinize=True) for n in left.names]
    right_list = [normalize(n, latinize=True) for n in right.names]
    for (left, right) in itertools.product(left_list, right_list):
        similarity = jaro(left, right)
        score = similarity * dampen(2, 20, shortest(left, right))
        result = max(result, score)
    return result


def compare_countries(left, right):
    left = left.country_hints
    right = right.country_hints
    overlap = left.intersection(right)
    return min(2.0, len(overlap))

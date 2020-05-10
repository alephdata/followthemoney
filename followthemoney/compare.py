import itertools
from typing import Dict
from followthemoney.types.common import PropertyType

from Levenshtein import jaro  # type: ignore
from normality import normalize  # type: ignore
from followthemoney.model import Model
from followthemoney.proxy import EntityProxy
from followthemoney.types import registry
from followthemoney.util import dampen, shortest
from followthemoney.util import ProxyData
from followthemoney.exc import InvalidData

# OK, Here's the plan: we have to find a way to get user judgements
# on as many of these matches as we can, then build a regression
# model which properly weights the value of a matching property
# based upon it's type.
NAMES_WEIGHT: float = 0.6
COUNTRIES_WEIGHT: float = 0.1
MATCH_WEIGHTS: Dict[PropertyType, float] = {
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


def compare(model: Model, left: ProxyData, right: ProxyData) -> float:
    """Compare two entities and return a match score."""
    entity_left = model.get_proxy(left)
    entity_right = model.get_proxy(right)
    if entity_right.schema not in list(entity_left.schema.matchable_schemata):
        return 0
    schema = model.common_schema(entity_left.schema, entity_right.schema)
    score = compare_names(entity_left, entity_right) * NAMES_WEIGHT
    score += compare_countries(entity_left, entity_right) * COUNTRIES_WEIGHT
    for name, prop in schema.properties.items():
        weight = MATCH_WEIGHTS.get(prop.type, 0)
        if weight == 0 or not prop.matchable:
            continue
        try:
            left_values = entity_left.get(name)
            right_values = entity_right.get(name)
        except InvalidData:
            continue

        if not len(left_values) or not len(right_values):
            continue
        prop_score = prop.type.compare_sets(left_values, right_values)
        score += (prop_score * weight)
    return score


def compare_names(left: EntityProxy, right: EntityProxy) -> float:
    result = 0
    left_list = [normalize(n, latinize=True) for n in left.names]
    right_list = [normalize(n, latinize=True) for n in right.names]
    for (left, right) in itertools.product(left_list, right_list):
        similarity = jaro(left, right)
        score = similarity * dampen(2, 20, shortest(left, right))
        result = max(result, score)
    return result


def compare_countries(left: EntityProxy, right: EntityProxy) -> float:
    left_set = left.country_hints
    right_set = right.country_hints
    overlap = left_set.intersection(right_set)
    return min(2.0, len(overlap))

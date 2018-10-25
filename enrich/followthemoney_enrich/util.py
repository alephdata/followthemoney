from banal import is_mapping
from urlnormalizer import normalize_url


def make_url(url, params):
    if is_mapping(params):
        params = params.items()
    if params is not None:
        url = normalize_url(url, extra_query_args=params)
    return url

from followthemoney.proxy import E

# Derived from: https://fsi.taxjustice.net/en/introduction/fsi-results
OFFSHORE_COUNTRIES = set(
    (
        "ky",
        "ch",
        "sg",
        "lu",
        "vg",
        "gg",
        "pa",
        "je",
        "mt",
        "bs",
        "cy",
        "gi",
        "mo",
        "bm",
        "im",
        "mh",
        "mu",
        "li",
        "ai",
        "kn",
        "tc",
        "vu",
        "mc",
        "sc",
        "ag",
        "dm",
        "ms",
        "lc",
        "ck",
    )
)


def offshore_from_jurisdiction(proxy: E) -> E:
    """Tag organizations linked to a well-known offshore jurisdiction as
    offshores automatically. Complete generalization, use only in experiments."""
    if not proxy.schema.is_a("Organization"):
        return proxy
    countries = set(proxy.get("country", quiet=True))
    countries.update(proxy.get("jurisdiction", quiet=True))
    if len(countries.intersection(OFFSHORE_COUNTRIES)) > 0:
        proxy.add("topics", "corp.offshore")
    return proxy

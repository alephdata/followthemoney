from pkg_resources import iter_entry_points


for ep in iter_entry_points('followthemoney.cli'):
    ep.load()

from importlib.metadata import entry_points


for ep in entry_points(group="followthemoney.cli"):
    ep.load()

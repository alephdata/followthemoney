import sys


def load_entry_points() -> None:
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 10:
        from importlib.metadata import entry_points

        for ep in entry_points().select(group="followthemoney.cli"):
            ep.load()
    else:
        from pkg_resources import iter_entry_points

        for ep_ in iter_entry_points("followthemoney.cli"):
            ep_.load()


load_entry_points()

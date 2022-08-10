import click
import datetime
from pathlib import Path
from typing import Iterable, Optional

from followthemoney import model
from followthemoney.proxy import E, EntityProxy
from followthemoney.types import registry
from followthemoney.cli.cli import cli
from followthemoney.cli.util import InPath, OutPath, path_entities
from followthemoney.cli.util import path_writer, write_entity


def get_possible_date(
        date_str: str,
        latest: bool = True
) -> datetime.date:
    """
    Returns date in datetime.date format.
    When date is incomplete, chooses the latest possible date if latest is true
    or the earliest possible date otherwise.
    """
    split_date = date_str.split("-")
    if len(split_date) == 3:  # Format is yyyy-mm-dd
        return datetime.date.fromisoformat(date_str)
    elif len(split_date) == 2:  # Format is yyyy-mm
        year, month = split_date
        if latest:
            day_month = (28 if year % 4 else 29) if month == "02" else \
                (30 if month in ["04", "06", "09", "11"] else 31)
        else:
            day_month = "01"
        return datetime.date.fromisoformat(date_str + f"-{day_month}")
    elif latest:  # Format is yyyy
        return datetime.date.fromisoformat(date_str + "-12-31")
    else:  # Format is yyyy
        return datetime.date.fromisoformat(date_str + "-01-01")


def filter_recent_entity(
    entity: EntityProxy,
    date: datetime.date,
    keep_only_last: bool,
    sieve: bool
) -> Optional[EntityProxy]:
    list_retrieved_at = entity.get("retrievedAt", quiet=True)
    if list_retrieved_at:
        max_retrieved_at = max(list_retrieved_at)
        retrieved_at_formatted = get_possible_date(max_retrieved_at)
        if date <= retrieved_at_formatted:
            if keep_only_last or sieve:
                entity.pop("retrievedAt")
            if keep_only_last:
                entity.add("retrievedAt", max_retrieved_at)
            return entity
    return None


@cli.command("filter_recent", help="Filter out entities that have an old retrievedAt prop (or none).")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
@click.option(
    "-d",
    "--date",
    help="Filter out entities retrieved before given date",
)
@click.option(
    "-n",
    "--days",
    type=int,
    help="Filter out entities retrieved before a certain number of days.",
)
@click.option(
    "--keep_only_last",
    is_flag=True,
    help="Keep only most recent retrievedAt property",
)
@click.option(
    "--sieve",
    is_flag=True,
    help="Delete retrievedAt property from entities",
)
def filter_recent(
    infile: Path,
    outfile: Path,
    date: str,
    days: int,
    keep_only_last: bool,
    sieve: bool
) -> None:
    if date and days:
        date_typed = get_possible_date(date, latest=False)
        last_update_date = min(date_typed, datetime.date.today() - datetime.timedelta(days=days))
    elif date:
        last_update_date = get_possible_date(date, latest=False)
    elif days:
        last_update_date = datetime.date.today() - datetime.timedelta(days=days)
    else:
        return

    try:
        with path_writer(outfile) as outfh:
            for entity in path_entities(infile, EntityProxy):
                filtered = filter_recent_entity(entity, last_update_date, keep_only_last, sieve)
                if filtered is not None:
                    write_entity(outfh, filtered)
    except BrokenPipeError:
        raise click.Abort()

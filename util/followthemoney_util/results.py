import click

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object, write_object


@cli.command('result-entities', help="Unnests results into entities")
def result_entities():
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            result = read_object(stdin)
            if result is None:
                break
            for entity in result.entities:
                write_object(stdout, entity)
    except BrokenPipeError:
        pass


@cli.command('filter-results', help="Filter results based on a recon file")
def filter_results():
    # try:
    #     stdin = click.get_text_stream('stdin')
    #     stdout = click.get_text_stream('stdout')
    #     while True:
    #         result = read_object(stdin)
    #         if result is None:
    #             break
    #         for entity in result.entities:
    #             write_object(stdout, entity)
    # except BrokenPipeError:
    #     pass
    pass

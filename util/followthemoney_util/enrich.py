import click

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object, write_object, load_enricher


@cli.command('enrich', help="Find matching entities remotely")
@click.argument('enricher')
def enrich(enricher):
    enricher = load_enricher(enricher)
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            has_result = False
            for result in enricher.enrich_entity(entity):
                has_result = True
                write_object(stdout, result)
            if not has_result:
                # emit the original entity anyways for streaming.
                result = enricher.make_result(entity)
                write_object(stdout, result)
    except BrokenPipeError:
        pass
    except Exception:
        raise
    finally:
        enricher.close()


@cli.command('expand', help="Expand enriched entities")
@click.argument('enricher')
def expand(enricher):
    enricher = load_enricher(enricher)
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            result = enricher.expand_entity(entity)
            write_object(stdout, result)
    except BrokenPipeError:
        pass
    except Exception:
        raise
    finally:
        enricher.close()

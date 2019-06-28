import json
import click
import logging
from pprint import pprint  # noqa

from followthemoney import model
from followthemoney.cli.cli import cli
from followthemoney.cli.util import write_object

log = logging.getLogger(__name__)
IDENTIFIERS = {
    'TRADE_REGISTER': 'registrationNumber',
    'TAX_ID': 'vatCode',
    'ORGANIZATION_ID': 'classification',
    'STATISTICAL': 'classification',
}


@cli.command('import-ocds', help="Import open contracting data")
def import_ocds():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            line = stdin.readline()
            if not line:
                return
            record = json.loads(line)
            for entity in convert_record(record):
                if entity.id is not None:
                    write_object(stdout, entity)
    except BrokenPipeError:
        raise click.Abort()


def clean_date(date):
    if date is not None and 'T' in date:
        date, _ = date.split('T', 1)
    return date


def make_address(*parts):
    return ' '.join((p for p in parts if p is not None))


def convert_party(party):
    entity = model.make_entity('LegalEntity')
    entity.make_id(party.pop('id', None))
    entity.add('name', party.pop('name', None))
    address = party.pop('address', {})
    entity.add('country', address.pop('countryName', None))
    address_text = make_address(address.pop('streetAddress', None),
                                address.pop('postalCode', None),
                                address.pop('region', None))
    entity.add('address', address_text)
    if len(address):
        log.info("Unknown address part: %r", address.keys())
    contact = party.pop('contactPoint', {})
    entity.add('website', contact.pop('url', None))
    entity.add('phone', contact.pop('telephone', None))
    entity.add('email', contact.pop('email', None))
    for identifier in party.pop('additionalIdentifiers', []):
        scheme = identifier.pop('scheme', None)
        prop = IDENTIFIERS.get(scheme, None)
        if prop is None:
            log.info("Unknown identifier scheme: %s", scheme)
            continue
        entity.add(prop, identifier.pop('id', None))
    # pprint(party)
    return entity


def convert_release(release):
    for party in release.pop('parties', []):
        yield convert_party(party)

    buyer = release.pop('buyer', {})
    authority = model.make_entity('LegalEntity')
    authority.make_id(buyer.pop('id', None))
    authority.add('name', buyer.pop('name', None))
    yield authority

    tender = release.pop('tender', {})
    contract = model.make_entity('Contract')
    contract.make_id(release.pop('id', None))
    contract.add('authority', authority)
    contract.add('name', tender.pop('title', None))
    if not contract.has('name'):
        contract.add('name', tender.get('id', None))

    contract.add('description', tender.pop('description', None))
    contract.add('procedureNumber', tender.pop('id', None))
    contract.add('type', tender.pop('mainProcurementCategory', None))
    value = tender.pop('value', {})
    contract.add('amount', value.pop('amount', None))
    contract.add('currency', value.pop('currency', None))
    # pprint(tender)
    yield contract

    # contract.add('modifiedAt', published_date)
    lots = tender.pop('lots', [])
    for award in release.pop('awards', []):
        ca = model.make_entity('ContractAward')
        ca.make_id(contract.id, award.pop('id', None))
        ca.add('contract', contract)
        ca.add('date', clean_date(award.pop('date', None)))
        value = award.pop('value', {})
        ca.add('amount', value.pop('amount', None))
        ca.add('currency', value.pop('currency', None))
        reason = tender.get('procurementMethodDetails', None)
        ca.add('decisionReason', reason)

        for document in award.pop('documents', []):
            ca.add('sourceUrl', document.get('url'))

        for item in award.pop('items', []):
            classification = item.pop('classification', {})
            ca.add('cpvCode', classification.get('url'))

        related_lots = award.pop('relatedLots', [])
        for lot in lots:
            if lot.get('id') in related_lots:
                ca.add('role', lot.get('title'))
                ca.add('summary', lot.get('description'))

        for supplier in award.pop('suppliers', []):
            entity = model.make_entity('LegalEntity')
            entity.make_id(supplier.pop('id', None))
            entity.add('name', supplier.pop('name', None))
            ca.add('supplier', entity)
            yield entity

        # pprint(award)
        yield ca


def convert_record(record):
    published_date = clean_date(record.pop('publishedDate', None))
    publisher = record.pop('publisher', {}).get('name')
    for release in record.get('releases', []):
        for entity in convert_release(release):
            entity.add('publisher', publisher, quiet=True)
            entity.add('modifiedAt', published_date, quiet=True)
            yield entity

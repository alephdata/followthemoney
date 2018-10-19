import logging
import requests
from time import sleep
from os import environ
from urllib import quote_plus
from itertools import count
from pprint import pprint  # noqa

from corpint.model.schema import PERSON, OTHER, ORGANIZATION, COMPANY

log = logging.getLogger(__name__)
API_KEY = environ.get('OPENCORPORATES_APIKEY')
OFFICER_SEARCH_API = 'https://api.opencorporates.com/v0.4/officers/search'
COMPANY_SEARCH_API = 'https://api.opencorporates.com/v0.4/companies/search'
GROUPING_API = 'https://api.opencorporates.com/corporate_groupings/%s'


def get_oc_api(url, params=None):
    if not url.startswith('https://api.openc'):
        url = url.replace('https://openc', 'https://api.openc')

    params = params or dict()
    params['api_token'] = API_KEY

    for i in count(2):
        try:
            res = requests.get(url, params=params, verify=False)
            return res.json().get('results')
        except Exception as ex:
            log.exception(ex)
            sleep(i ** 2)


def emit_officer(emitter, officer, company_url=None, publisher=None):
    if isinstance(officer.get('officer'), dict):
        officer = officer.get('officer')

    company = officer.get('company')
    if company_url is None and company is not None:
        company_url = company.get('opencorporates_url')
        # always download full company records.
        get_company(emitter, company_url)

    emitter.log.info("OC Officer [%(id)s]: %(name)s", officer)
    officer_uid = emitter.uid(officer['opencorporates_url'])
    emitter.emit_entity({
        'uid': officer_uid,
        'name': officer['name'],
        'dob': officer.get('date_of_birth'),
        'country': officer.get('nationality'),
        'summary': officer.get('occupation'),
        'opencorporates_url': officer['opencorporates_url'],
        'publisher': publisher
    })

    if company_url is not None:
        company_uid = emitter.uid(company_url)
        emitter.emit_link({
            'source_uid': company_uid,
            'target_uid': officer_uid,
            'publisher': publisher,
            'summary': officer.get('position'),
            'start_date': officer.get('start_date'),
            'end_date': officer.get('end_date'),
            'source_url': officer['opencorporates_url']
        })
    return officer_uid


def emit_company(emitter, company):
    if isinstance(company.get('company'), dict):
        company = company.get('company')

    company_url = company['opencorporates_url']
    company_uid = emitter.uid(company_url)
    source = company.get('source', {})
    publisher = source.get('publisher')

    aliases = set()
    for key in ['alternative_names', 'previous_names']:
        for value in company.get(key, []):
            value = value.get('company_name')
            if value is not None:
                aliases.add(value)

    emitter.log.info("OC Company [%(company_number)s]: %(name)s", company)
    emitter.emit_entity({
        'uid': company_uid,
        'name': company.get('name'),
        'aliases': aliases,
        'schema': 'Company',
        'publisher': publisher,
        'registration_number': company.get('company_number'),
        'country': company.get('jurisdiction_code')[:2].upper(),
        'legal_form': company.get('company_type'),
        'status': company.get('current_status'),
        'dissolution_date': company.get('dissolution_date'),
        'incorporation_date': company.get('incorporation_date'),
        'opencorporates_url': company.get('opencorporates_url'),
        'address': company.get('registered_address_in_full'),
    })

    for officer in company.get('officers', []):
        emit_officer(emitter, officer, company_url=company_url,
                     publisher=publisher)

    return company_uid


def get_company(emitter, opencorporates_url):
    company_uid = emitter.uid(opencorporates_url)
    if emitter.entity_exists(company_uid):
        return company_uid
    company = get_oc_api(opencorporates_url)
    if company is not None:
        return emit_company(emitter, company)


def get_officer(emitter, opencorporates_url):
    officer_uid = emitter.uid(opencorporates_url)
    if emitter.entity_exists(officer_uid):
        return officer_uid
    officer = get_oc_api(opencorporates_url)
    if office is not None:
        return emit_officer(emitter, officer)


def get_grouping(origin, name):
    url = GROUPING_API % quote_plus(name)
    origin.log.info("Loading grouping from: %s", url)
    results = get_oc_api(url)
    grouping = results.get('corporate_grouping')
    memberships = grouping.pop('memberships', [])
    for membership in memberships:
        membership = membership.get('membership')
        company = membership.get('company')
        get_company(origin, company.get('opencorporates_url'))


def search_officers(origin, entity):
    for page in count(1):
        # TODO aliases
        params = {
            'q': entity.name,
            'page': page
        }
        results = get_oc_api(OFFICER_SEARCH_API, params=params)
        if results is None:
            break
        for officer in results.get('officers'):
            officer = officer.get('officer')
            url = officer.get('opencorporates_url')
            emitter = origin.result(entity.uid, origin.uid(url))
            emit_officer(emitter, officer)
        if page >= results.get('total_pages') or page >= 5:
            return


def search_companies(origin, entity):
    for page in count(1):
        # TODO aliases
        params = {
            'q': entity.name,
            'page': page
        }
        if entity.country:
            params['country_code'] = entity.country.lower()
        results = get_oc_api(COMPANY_SEARCH_API, params=params)
        if results is None:
            break
        for company in results.get('companies'):
            company = company.get('company')
            url = company.get('opencorporates_url')
            company_uid = origin.uid(url)
            emitter = origin.result(entity.uid, company_uid)
            get_company(emitter, url)
        if page >= results.get('total_pages'):
            return


def enrich(origin, entity):
    origin.log.info('Search OC [%s]: %s', entity.schema, entity.name)
    if entity.schema in [OTHER, ORGANIZATION, COMPANY, PERSON]:
        search_officers(origin, entity)
    if entity.schema in [OTHER, ORGANIZATION, COMPANY]:
        search_companies(origin, entity)

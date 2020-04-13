import os
import logging
import requests
from banal import ensure_list, ensure_dict
from requests.exceptions import RequestException

from followthemoney import model
from followthemoney_enrich.enricher import Enricher
from followthemoney_enrich.util import make_url

log = logging.getLogger(__name__)


class OpenCorporatesEnricher(Enricher):
    COMPANY_SEARCH_API = 'https://api.opencorporates.com/v0.4/companies/search'
    OFFICER_SEARCH_API = 'https://api.opencorporates.com/v0.4/officers/search'
    COMPANY_NO_API = 'https://api.opencorporates.com/v0.4/companies/'
    GROUPING_API = 'https://api.opencorporates.com/v0.4/corporate_groupings/search'  # noqa

    def __init__(self):
        self.session = requests.Session()
        self.api_token = os.environ.get('ENRICH_OPENCORPORATES_API_TOKEN')
        if self.api_token is None:
            log.warning("OpenCorporates enricher has no API token")

    def get_api(self, url, params=None):
        url = url.replace('https://opencorporates.com/',
                          'https://api.opencorporates.com/v0.4/')
        url = make_url(url, params)
        if self.cache.has(url):
            return self.cache.get(url)

        auth = {'api_token': self.api_token}
        try:
            log.info("Enrich: %s", url)
            res = self.session.get(url, params=auth)
            if res.status_code != 200:
                log.warning("Non-200 response: %s", res.content)
                return {}
            data = res.json()
        except RequestException:
            log.exception("OpenCorporates API Error")
            return {}
        self.cache.store(url, data)
        if 'error' in data:
            return {}
        return data

    def company_entity(self, data, entity=None):
        if 'company' in data:
            data = ensure_dict(data.get('company', data))
        if entity is None:
            entity = model.make_entity('Company')
            entity.make_id(data.get('opencorporates_url'))
        entity.add('name', data.get('name'))
        address = ensure_dict(data.get('registered_address'))
        entity.add('country', address.get('country'))
        entity.add('jurisdiction', data.get('jurisdiction_code'))
        entity.add('alias', data.get('alternative_names'))
        entity.add('address', data.get('registered_address_in_full'))
        entity.add('sourceUrl', data.get('registry_url'))
        entity.add('legalForm', data.get('company_type'))
        entity.add('incorporationDate', data.get('incorporation_date'))
        entity.add('dissolutionDate', data.get('dissolution_date'))
        entity.add('status', data.get('current_status'))
        entity.add('registrationNumber', data.get('company_number'))
        entity.add('opencorporatesUrl', data.get('opencorporates_url'))
        source = data.get('source', {})
        entity.add('publisher', source.get('publisher'))
        entity.add('publisherUrl', source.get('url'))
        entity.add('retrievedAt', source.get('retrieved_at'))
        for code in ensure_list(data.get('industry_codes')):
            code = code.get('industry_code', code)
            entity.add('sector', code.get('description'))
        for previous in ensure_list(data.get('previous_names')):
            entity.add('previousName', previous.get('company_name'))
        for alias in ensure_list(data.get('alternative_names')):
            entity.add('alias', alias.get('company_name'))
        return entity

    def officer_entity(self, data, entity=None):
        if 'officer' in data:
            data = ensure_dict(data.get('officer', data))
        person = data.get('occupation') or data.get('date_of_birth')
        schema = 'Person' if person else 'LegalEntity'
        entity = model.make_entity(schema)
        entity.make_id(data.get('opencorporates_url'))
        entity.add('name', data.get('name'))
        entity.add('country', data.get('nationality'))
        entity.add('jurisdiction', data.get('jurisdiction_code'))
        entity.add('address', data.get('address'))
        entity.add('birthDate', data.get('date_of_birth'), quiet=True)
        entity.add('position', data.get('occupation'), quiet=True)
        entity.add('opencorporatesUrl', data.get('opencorporates_url'))
        source = data.get('source', {})
        entity.add('publisher', source.get('publisher'))
        entity.add('publisherUrl', source.get('url'))
        entity.add('retrievedAt', source.get('retrieved_at'))
        return entity

    def get_query(self, entity):
        params = {'q': entity.caption}
        for jurisdiction in entity.get('jurisdiction'):
            params['jurisdiction_code'] = jurisdiction.lower()
        return params

    def search_companies(self, entity):
        params = self.get_query(entity)
        for page in range(1, 9):
            params['page'] = page
            results = self.get_api(self.COMPANY_SEARCH_API, params=params)
            companies = results.get('results', {}).get('companies')
            for company in ensure_list(companies):
                proxy = self.company_entity(company)
                yield self.make_match(entity, proxy)
            if page >= results.get('total_pages', 0):
                break

    def search_officers(self, entity):
        params = self.get_query(entity)
        for page in range(1, 9):
            params['page'] = page
            results = self.get_api(self.OFFICER_SEARCH_API, params=params)
            officers = results.get('results', {}).get('officers')
            for officer in ensure_list(officers):
                proxy = self.officer_entity(officer)
                yield self.make_match(entity, proxy)
            if page >= results.get('total_pages', 0):
                break

    def enrich_entity(self, entity):
        if self.api_token is None:
            return
        schema = entity.schema.name
        if schema in ['Company', 'Organization', 'LegalEntity']:
            yield from self.search_companies(entity)
        if schema in ['Person', 'LegalEntity', 'Company', 'Organization']:
            yield from self.search_officers(entity)

    def expand_company(self, entity, data):
        data = ensure_dict(data.get('company', data))
        entity = self.company_entity(data, entity=entity)
        for officer in ensure_list(data.get('officers')):
            yield from self.expand_officer(officer, company=entity)
        yield entity

    def expand_officer(self, data, entity=None, company=None):
        data = ensure_dict(data.get('officer', data))
        entity = self.officer_entity(data, entity=entity)
        yield entity

        company = self.company_entity(data.get('company'), entity=company)
        yield company

        if company.id and entity.id:
            directorship = model.make_entity('Directorship')
            directorship.make_id(data.get('opencorporates_url'),
                                 'Directorship')
            directorship.add('director', entity.id)
            directorship.add('startDate', data.get('start_date'))
            directorship.add('endDate', data.get('end_date'))
            directorship.add('organization', company.id)
            directorship.add('role', data.get('position'))
            yield directorship

    def expand_entity(self, entity):
        for url in entity.get('opencorporatesUrl', quiet=True):
            data = self.get_api(url).get('results', {})
            if 'company' in data:
                yield from self.expand_company(entity, data)
            if 'officer' in data:
                yield from self.expand_officer(data, officer=entity)

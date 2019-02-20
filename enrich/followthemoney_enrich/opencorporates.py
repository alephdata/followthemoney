import os
import logging
import requests
from banal import ensure_list, ensure_dict
from requests.exceptions import RequestException

from followthemoney_enrich.enricher import Enricher
from followthemoney_enrich.util import make_url

log = logging.getLogger(__name__)


class OpenCorporatesEnricher(Enricher):
    key_prefix = 'opencorporates'

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

    def company_entity(self, result, data):
        data = ensure_dict(data.get('company', data))
        entity = result.make_entity('Company')
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
        for officer in ensure_list(data.get('officers')):
            self.officer_entity(result, officer, company=entity)
        return entity

    def officer_entity(self, result, data, company=None):
        data = ensure_dict(data.get('officer', data))
        person = data.get('occuptation') or data.get('date_of_birth')
        schema = 'Person' if person else 'LegalEntity'
        officer = result.make_entity(schema)
        officer.make_id(data.get('opencorporates_url'))
        officer.add('name', data.get('name'))
        officer.add('country', data.get('nationality'))
        officer.add('jurisdiction', data.get('jurisdiction_code'))
        officer.add('address', data.get('address'))
        officer.add('birthDate', data.get('date_of_birth'), quiet=True)
        officer.add('position', data.get('occupation'), quiet=True)
        officer.add('opencorporatesUrl', data.get('opencorporates_url'))
        source = data.get('source', {})
        officer.add('publisher', source.get('publisher'))
        officer.add('publisherUrl', source.get('url'))
        officer.add('retrievedAt', source.get('retrieved_at'))

        if company is None:
            company = self.company_entity(result, data.get('company'))

        if company.id and officer.id:
            directorship = result.make_entity('Directorship')
            directorship.make_id(data.get('opencorporates_url'),
                                 'Directorship')
            directorship.add('director', officer.id)
            directorship.add('startDate', data.get('start_date'))
            directorship.add('endDate', data.get('end_date'))
            directorship.add('organization', company.id)
            directorship.add('role', data.get('position'))
        return officer

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
                result = self.make_result(entity)
                proxy = self.company_entity(result, company)
                result.set_candidate(proxy)
                yield result
            if page >= results.get('total_pages', 0):
                break

    def search_officers(self, entity):
        params = self.get_query(entity)
        for page in range(1, 9):
            params['page'] = page
            results = self.get_api(self.OFFICER_SEARCH_API, params=params)
            officers = results.get('results', {}).get('officers')
            for officer in ensure_list(officers):
                result = self.make_result(entity)
                proxy = self.officer_entity(result, officer)
                result.set_candidate(proxy)
                yield result
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

    def expand_entity(self, entity):
        result = super(OpenCorporatesEnricher, self).expand_entity(entity)
        for url in entity.get('opencorporatesUrl', quiet=True):
            data = self.get_api(url).get('results', {})
            if 'company' in data:
                self.company_entity(result, data)
            if 'officer' in data:
                self.officer_entity(result, data)
        return result

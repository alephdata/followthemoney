import os
import logging
import requests
from urlnormalizer import normalize_url
from banal import ensure_list, ensure_dict, is_mapping

from corpint.common import Enricher, Result

log = logging.getLogger(__name__)


class OpenCorporatesEnricher(Enricher):
    key_prefix = 'opencorporates'

    COMPANY_SEARCH_API = 'https://api.opencorporates.com/v0.4/companies/search'
    OFFICER_SEARCH_API = 'https://api.opencorporates.com/v0.4/officers/search'
    COMPANY_NO_API = 'https://api.opencorporates.com/v0.4/companies/'
    GROUPING_API = 'https://api.opencorporates.com/v0.4/corporate_groupings/search'  # noqa

    def __init__(self):
        self.session = requests.Session()
        self.api_token = os.environ.get('CORPINT_OPENCORPORATES_API_TOKEN')
        if self.api_token is None:
            log.warning("OpenCorporates enricher has no API token")

    def get_api(self, url, params=None):
        if not url.startswith('https://api.openc'):
            url = url.replace('https://openc', 'https://api.openc')

        if is_mapping(params):
            params = params.items()
        if params is not None:
            url = normalize_url(url, extra_query_args=params)

        data = self.cache.get(url)
        if data is None:
            auth = {'api_token': self.api_token}
            res = self.session.get(url, params=auth)
            if res.status_code != 200:
                return {}
            data = res.json()
            self.cache.store(url, data)
        if 'error' in data:
            return {}
        return data.get('results')

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
        entity.add('sector', data.get('industry_codes'))
        entity.add('registrationNumber', data.get('company_number'))
        entity.add('opencorporatesUrl', data.get('opencorporates_url'))
        # entity.add('parent', data.get('controlling_entity'))
        for previous in ensure_list(data.get('previous_names')):
            entity.add('previousName', previous.get('company_name'))
        for officer in ensure_list(data.get('officers')):
            self.officer_entity(result, officer, company=entity)
        return entity

    def officer_entity(self, result, data, company=None):
        data = ensure_dict(data.get('officer', data))
        officer = result.make_entity('Person')
        officer.make_id(data.get('opencorporates_url'))
        officer.add('name', data.get('name'))
        officer.add('country', data.get('nationality'))
        officer.add('jurisdiction', data.get('jurisdiction_code'))
        officer.add('address', data.get('address'))
        officer.add('birthDate', data.get('date_of_birth'))
        officer.add('opencorporatesUrl', data.get('opencorporates_url'))
        # officer.add('idNumber', data.get('id'))

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

    def search_companies(self, params):
        for page in range(1, 9):
            # TODO aliases
            params['page'] = page
            results = self.get_api(self.COMPANY_SEARCH_API, params=params)
            for company in ensure_list(results.get('companies')):
                result = Result(self)
                result.principal = self.company_entity(result, company)
                yield result
            if page > results.get('total_pages', 1):
                break

    def search_officers(self, params):
        for page in range(1, 9):
            # TODO aliases
            params['page'] = page
            results = self.get_api(self.OFFICER_SEARCH_API, params=params)
            for officer in ensure_list(results.get('officers')):
                result = Result(self)
                result.principal = self.officer_entity(result, officer)
                yield result
            if page > results.get('total_pages', 1):
                break

    def enrich_entity(self, entity):
        if self.api_token is None:
            return

        name = ' OR '.join(entity.names)
        params = {'q': name}
        for jurisdiction in entity.get('jurisdiction'):
            params['jurisdiction_code'] = jurisdiction.lower()

        schema = entity.schema.name
        if schema in ['Company', 'Organization', 'LegalEntity']:
            yield from self.search_companies(params)
        if schema in ['Person', 'LegalEntity', 'Company', 'Organization']:
            # officer search for companies??
            yield from self.search_officers(params)

from os import environ
from lxml import etree
from collections import defaultdict
from pprint import pprint  # noqa
import zeep
from zeep.exceptions import TransportError

from corpint.model.schema import PERSON, COMPANY, ORGANIZATION, OTHER

WSDL = 'https://webservices.bvdep.com/orbis/remoteaccess.asmx?WSDL'
USERNAME = environ.get('ORBIS_USERNAME', 'occrp_ws')
PASSWORD = environ.get('ORBIS_PASSWORD')

FIELD_MAPPING = {
    'STATUS': 'status',
    'SLEGALF': 'legal_form',
    'LEGALFRM': 'legal_form',
    'RELEASE_DATE': 'last_updated',
    'SOURCE_IP_NAME': 'publisher',
    # 'DATASET': 'publisher',
    # 'STATEINC': 'jurisdiction',
    'DATEINC': 'incorporation_date',
    'NAME': 'name',
    'CPYCONTACTS_HEADER_FullNameOriginalLanguagePreferred': 'name',
    '-9006': 'bvd_id',
    '-9105': 'bvd_id',
    '-9305': 'bvd_id',
    'CPYCONTACTS_HEADER_IdDirector': 'bvd_id',
    '-9003': 'country',
    '-9102': 'country',
    '-9302': 'country',
    'CPYCONTACTS_HEADER_MultipleNationalitiesLabel': 'country',
    'CPYCONTACTS_HEADER_CountryLabel': 'country',
    'DESCHIST': 'summary',
    'SUBSIDIARIES_LEI': 'lei',
    '-9001': 'name',
    '-9300': 'name',
    '-32139': 'name',
    '-9015': 'type',
    '-9059': 'type',
    '-9314': 'type',
    'CPYCONTACTS_HEADER_Type': 'type',
    'NAME_INTERNAT': 'aliases',
    'SHAREHOLDERS_NAMEONLYASCII': 'aliases',
    'SUBSIDIARIES_NAMEONLYASCII': 'aliases',
    '-32117': 'aliases',
    'SHAREHOLDERS_FIRSTNAME': 'first_name',
    '-32124': 'first_name',
    'CPYCONTACTS_HEADER_FirstNameOriginalLanguagePreferred': 'first_name',
    'SHAREHOLDERS_LASTNAME': 'last_name',
    '-32125': 'last_name',
    'CPYCONTACTS_HEADER_LastNameOriginalLanguagePreferred': 'last_name',
    'CPYCONTACTS_HEADER_MiddleNameOriginalLanguagePreferred': 'middle_name',
    'CPYCONTACTS_HEADER_Birthdate': 'dob',
    '-9083': 'industry',
    '-32056': 'industry',
    '-9009': 'percentage',
    '-9108': 'percentage',
    '-9308': 'percentage',
    '-9010': 'percentage_total',
    '-9109': 'percentage_total',
    '-9309': 'percentage_total',
    '-9033': 'start_date',
    '-9132': 'start_date',
    '-9332': 'start_date',
    'CPYCONTACTS_MEMBERSHIP_BeginningNominationDate': 'start_date',
    'CPYCONTACTS_MEMBERSHIP_DepartmentFromHierCodeFall2009': 'role',
    'CPYCONTACTS_MEMBERSHIP_Function': 'role',
    'CPYCONTACTS_MEMBERSHIP_FunctionOriginalOriginalLanguagePreferred': 'summary'  # noqa
}

LINK_FIELDS = ['role', 'percentage', 'percentage_total', 'start_date',
               'end_date']

TYPES = {
    'Individual': PERSON,
    'One or more named individuals or families': PERSON,
    'Unnamed private shareholders, aggregated': PERSON,
    'Industrial company': COMPANY,
    'Private Equity firms': COMPANY,
    'Bank': COMPANY,
    'Financial company': COMPANY,
    'Venture capital': COMPANY,
    'Mutual & Pension Fund/Nominee/Trust/Trustee': ORGANIZATION,
    'Public authority, State, Government': ORGANIZATION,
    'Insurance company': COMPANY,
    'Company': COMPANY,
}


def parse_xml(res):
    res = res.replace('xmlns="', 'xmlnons="')
    doc = etree.fromstring(res.encode('utf-8'))

    # for record in doc.findall('.//record'):
    #     UNKNOWN = defaultdict(list)
    #     items = defaultdict(list)
    #     for item in record.findall('./item'):
    #         field = item.get('field')
    #         prop = FIELD_MAPPING.get(field)
    #         if prop is not None:
    #             continue
    #         if item.text and len(item.text.strip()):
    #             print field, item.text.strip()
    #         for child in item.findall('./childItem'):
    #             if child.text and len(child.text.strip()):
    #                 print field, child.text.strip()
    #     pprint(dict(UNKNOWN))

    for record in doc.findall('.//record'):
        items = defaultdict(list)
        for item in record.findall('./item'):
            prop = FIELD_MAPPING.get(item.get('field'))
            if prop is None:
                continue
            if item.text and len(item.text.strip()):
                items[0].append((prop, item.text))
            for child in item.findall('./childItem'):
                index = child.get('index')
                items[index].append((prop, child.text))
        return items.values()
    return []


def get_list_data(client, session, res, format):
    res = client.service.GetListData(session, res, 0, 2000, format,
                                     'XML_UTF8')
    return parse_xml(res)


def get_section(client, session, res, section):
    res = client.service.GetReportSection(session, res, 0, 2000,
                                          section, 'USD', 'XML_UTF8')
    return parse_xml(res)


def link_items(emitter, entity, items, summary):
    other = {'aliases': set()}
    link = {'summary': summary}
    for key, value in items:
        if key in LINK_FIELDS:
            if key == 'role':
                key = 'summary'
            link[key] = value
            continue
        if key == 'aliases':
            other['aliases'].add(value)
        elif key == 'type':
            other['schema'] = TYPES.get(value)
            if other['schema'] is None and value is not None:
                print 'UNKOWN TYPE', [value]
        else:
            other[key] = value
    uid = other.get('bvd_id') or other.get('name')
    if uid is None:
        return
    other['uid'] = emitter.uid(uid)
    other['name'] = other['name'].replace('via its funds', '')
    emitter.log.info("Associated: %(name)s", other)
    emitter.emit_entity(other)
    link['source_uid'] = entity['uid']
    link['target_uid'] = other['uid']
    emitter.emit_link(link)


def emit_company(emitter, client, session, data):
    if data.Hint in ['UnlikelyCandidate']:
        return
    entity = {
        'uid': emitter.uid(data.BvDID),
        'name': data.Name,
        'bvd_id': data.BvDID,
        'schema': 'Company',
        'country': data.Country,
        'phone': data.PhoneOrFax,
        'registration_number': data.NationalId,
        'aliases': set(),
    }
    if data.NameInLocalAlphabet:
        entity['aliases'].add(data.NameInLocalAlphabet)

    SelectionResult = client.get_type('ns0:SelectionResult')
    res = SelectionResult(Token='BVDID{%s}' % data.BvDID, SelectionCount=1)

    for item in get_section(client, session, res, 'STATUS'):
        for key, value in item:
            if key in ['aliases']:
                entity[key].add(value)
            else:
                entity[key] = value

    emitter.log.info("Company [%(bvd_id)s]: %(name)s", entity)
    emitter.emit_entity(entity)

    for section in ['CONTROLLINGSHAREHOLDERS', 'CURRENTSHAREHOLDERS',
                    'SHAREHOLDERSHISTORY']:
        for item in get_section(client, session, res, section):
            link_items(emitter, entity, item, section)

    # for section in ['CONTACTS_CURR', 'CONTACTS_PREV']:
    #     for item in get_section(client, session, res, section):
    #         pprint(item)

    # FIXME: for some reason the orbis API will not return directors sections.
    # this workaround is dependent on setting up a specific list type, called
    # directors, in your orbis account.
    for item in get_list_data(client, session, res, 'Directors'):
        link_items(emitter, entity, item, 'Contact')

    for item in get_section(client, session, res, 'CURRENTSUBSIDIARIES'):
        link_items(emitter, entity, item, 'Subsidiary')


def enrich(origin, entity):
    if entity.schema not in [OTHER, ORGANIZATION, COMPANY]:
        origin.log.info('Orbis skip: %s', entity.name)
        return

    if PASSWORD is None:
        origin.log.warning('$ORBIS_PASSWORD not set, skipping BvD Orbis.')
        return

    client = zeep.Client(wsdl=WSDL)
    session = client.service.Open(USERNAME, PASSWORD)
    origin.log.info('Session [%s]: %s', session, entity.name)
    try:
        # print client.service.GetReportSectionIds(session)
        # print client.service.GetAvailableModels(session)

        MatchCriteria = client.get_type('ns0:MatchCriteria')
        ct = MatchCriteria(Name=entity.name, Country=entity.country)
        res = client.service.Match(session, ct, ['None'])
        if res is not None:
            for data in res:
                match_uid = origin.uid(data.BvDID)
                emitter = origin.result(entity.uid, match_uid)
                emit_company(emitter, client, session, data)
    except TransportError as terr:
        origin.log.exception(terr)
    finally:
        client.service.Close(session)

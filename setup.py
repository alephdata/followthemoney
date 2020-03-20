from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='followthemoney',
    version='1.27.6',
    author='Organized Crime and Corruption Reporting Project',
    author_email='data@occrp.org',
    url='https://docs.alephdata.org/developers/followthemoney',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=True,
    package_data={
        '': ['followthemoney/schema/*', 'followthemoney/translations/*']
    },
    zip_safe=False,
    install_requires=[
        'babel',
        'banal >= 0.4.2',
        'click >= 7.0',
        'stringcase >= 1.2.0',
        'pyyaml >= 5.1',
        'requests >= 2.21.0',
        'python-levenshtein >= 0.12.0',
        'normality >= 2.0.0',
        'sqlalchemy >= 1.2.0',
        'countrynames >= 1.6.0',
        'languagecodes >= 1.0.4',
        'phonenumbers >= 8.9.11',
        'python-stdnum >= 1.10',
        'urlnormalizer >= 1.2.0',
        'pantomime >= 0.3.2',
        'pytz >= 2018.5',
        'rdflib >= 4.2.2',
        'networkx >= 2.4',
        'openpyxl >= 3.0.3',
        'ordered-set >= 3.1.1',
    ],
    extras_require={
        'dev': [
            'pip>=10.0.0',
            'bumpversion>=0.5.3',
            'wheel>=0.29.0',
            'twine',
            'flake8>=2.6.0',
            'nose',
            'transifex-client',
            'responses>=0.9.0',
            'coverage>=4.1',
            'recommonmark>=0.4.0'
        ]
    },
    test_suite='nose.collector',
    entry_points={
        'babel.extractors': {
            'ftmmodel = followthemoney.messages:extract_yaml'
        },
        'followthemoney.types': {
            'url = followthemoney.types.url:UrlType',
            'name = followthemoney.types.name:NameType',
            'domain = followthemoney.types.domain:DomainType',
            'email = followthemoney.types.email:EmailType',
            'ip = followthemoney.types.ip:IpType',
            'iban = followthemoney.types.iban:IbanType',
            'address = followthemoney.types.address:AddressType',
            'date = followthemoney.types.date:DateType',
            'phone = followthemoney.types.phone:PhoneType',
            'country = followthemoney.types.country:CountryType',
            'language = followthemoney.types.language:LanguageType',
            'mimetype = followthemoney.types.mimetype:MimeType',
            'checksum = followthemoney.types.checksum:ChecksumType',
            'identifier = followthemoney.types.identifier:IdentifierType',
            'entity = followthemoney.types.entity:EntityType',
            'topic = followthemoney.types.topic:TopicType',
            'json = followthemoney.types.json:JsonType',
            'text = followthemoney.types.string:TextType',
            'html = followthemoney.types.string:HTMLType',
            'string = followthemoney.types.string:StringType',
            'number = followthemoney.types.number:NumberType'
        },
        'followthemoney.cli': {
            'aggregate = followthemoney.cli.aggregate:aggregate',
            'sieve = followthemoney.cli.sieve:sieve',
            'ocds = followthemoney.cli.ocds:import_ocds',
            'mapping = followthemoney.cli.mapping:run_mapping',
            'csv = followthemoney.cli.exports:export_csv',
            'excel = followthemoney.cli.exports:export_excel',
            'rdf = followthemoney.cli.exports:export_rdf',
            'gexf = followthemoney.cli.exports:export_gexf',
            'cypher = followthemoney.cli.exports:export_cypher',
        },
        'console_scripts': [
            'ftmutil = followthemoney.cli.cli:cli',
            'ftm = followthemoney.cli.cli:cli',
        ]
    },
    tests_require=['coverage', 'nose']
)

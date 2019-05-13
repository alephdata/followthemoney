from setuptools import setup, find_packages

setup(
    name='followthemoney',
    version='1.12.1',
    long_description="Data model and validator for investigative graph data.",
    author='Organized Crime and Corruption Reporting Project',
    author_email='data@occrp.org',
    url='https://occrp.org',
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
        'stringcase',
        'pyyaml >= 5.1',
        'requests[security] >= 2.21.0',
        'python-levenshtein >= 0.12.0',
        'normality >= 1.0.0',
        'sqlalchemy >= 1.2.0',
        'countrynames >= 1.6.0',
        'languagecodes >= 1.0.4',
        'phonenumbers >= 8.9.11',
        'python-stdnum >= 1.10',
        'urlnormalizer >= 1.2.0',
        'pantomime >= 0.3.2',
        'pytz >= 2018.5',
        'rdflib >= 4.1',
        'networkx >= 2.2',
        'openpyxl >= 2.6.0',
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
            'json = followthemoney.types.json:JsonType',
            'text = followthemoney.types.text:TextType',
            'string = followthemoney.types.string:StringType',
            'number = followthemoney.types.number:NumberType'
        }
    },
    tests_require=['coverage', 'nose']
)

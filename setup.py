from setuptools import setup, find_packages

setup(
    name='followthemoney',
    version='1.4.0',
    long_description="Data model and validator for investigative graph data.",
    author='Organized Crime and Corruption Reporting Project',
    author_email='pudo@occrp.org',
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
        'banal >= 0.4.0',
        'pyyaml >= 3.13',
        'requests[security] >= 2.20.0',
        'python-levenshtein >= 0.12.0',
        'normality >= 0.6.1',
        'sqlalchemy >= 1.2.0',
        'countrynames >= 1.6.0',
        'languagecodes >= 1.0.4',
        'phonenumbers >= 8.9.11',
        'schwifty >= 2018.4.1',
        'urlnormalizer >= 1.2.0',
        'pytz >= 2018.5',
        'rdflib >= 4.1',
        'networkx >= 2.2'
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
            'identifier = followthemoney.types.identifier:IdentifierType',
            'entity = followthemoney.types.entity:EntityType',
            'text = followthemoney.types.text:TextType',
            'string = followthemoney.types.string:StringType',
            'number = followthemoney.types.number:NumberType'
        }
    },
    tests_require=['coverage', 'nose']
)

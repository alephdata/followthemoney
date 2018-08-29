from setuptools import setup, find_packages

setup(
    name='followthemoney',
    version='1.1.0',
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
        'banal',
        'pyyaml',
        'requests[security] >= 2.18.4',
        'normality >= 0.6.1',
        'sqlalchemy >= 1.1.14',
        'countrynames >= 1.6.0',
        'languagecodes >= 1.0.4',
        'phonenumbers >= 8.9.11',
        'schwifty >= 2018.4.1',
        'urlnormalizer >= 1.2.0',
        'pytz >= 2018.5',
        'rdflib >= 4.1'
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
        }
    },
    tests_require=['coverage', 'nose']
)

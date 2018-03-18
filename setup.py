from setuptools import setup, find_packages

setup(
    name='followthemoney',
    version='0.6.5',
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
        'backports.csv',
        'babel',
        'six >= 1.11.0',
        'pyyaml',
        'requests[security] >= 2.18.4',
        'normality >= 0.5.1',
        'sqlalchemy >= 1.1.14',
        'exactitude >= 2.0.0',
        'rdflib'
    ],
    test_suite='nose.collector',
    entry_points={
        'babel.extractors': {
            'ftmmodel = followthemoney.messages:extract_yaml'
        }
    },
    tests_require=['coverage', 'nose']
)

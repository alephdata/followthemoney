from setuptools import setup, find_packages

setup(
    name='followthemoney-enrich',
    version='1.12.0',
    long_description="Data enrichment toolkit",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='',
    author='OCCRP',
    author_email='data@occrp.org',
    url='https://occrp.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'followthemoney',
        'mwclient',  # wikipedia
        'rdflib',  # wikidata
        'SPARQLWrapper',  # wikidata
        'zeep',  # bvd orbis (soap)
        'requests',
        'alephclient'
    ],
    entry_points={
        'followthemoney_enrich': [
            'aleph = followthemoney_enrich.aleph:AlephEnricher',
            'occrp = followthemoney_enrich.aleph:OccrpEnricher',
            'orbis = followthemoney_enrich.orbis:OrbisEnricher',
            'opencorporates = followthemoney_enrich.opencorporates:OpenCorporatesEnricher',  # noqa
        ],
    },
    test_suite='nose.collector',
    tests_require=['coverage', 'nose']
)

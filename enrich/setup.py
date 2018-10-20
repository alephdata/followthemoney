from setuptools import setup, find_packages

setup(
    name='followthemoney-enrich',
    version='0.1',
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
        'followthemoney >= 1.3.3',
        'mwclient',  # wikipedia
        'rdflib',  # wikidata
        'SPARQLWrapper',  # wikidata
        'zeep',  # bvd orbis (soap)
        'requests'
    ],
    test_suite='nose.collector',
    tests_require=['coverage', 'nose']
)

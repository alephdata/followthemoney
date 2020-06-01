from setuptools import setup, find_packages

setup(
    name='followthemoney-enrich',
    version='1.31.4',
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
        'alephclient',
        'requests',
        'redis',
    ],
    entry_points={
        'followthemoney.enrich': [
            'aleph = followthemoney_enrich.aleph:AlephEnricher',
            'opencorporates = followthemoney_enrich.opencorporates:OpenCorporatesEnricher',  # noqa
        ],
        'followthemoney.cli': [
            'enrich = followthemoney_enrich.cli:enrich',
        ],
    },
    test_suite='nose.collector',
    tests_require=['coverage', 'nose']
)

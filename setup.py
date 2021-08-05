from setuptools import setup, find_packages  # type: ignore

with open("README.md") as f:
    long_description = f.read()

setup(
    name="followthemoney",
    version="2.6.0",
    author="Organized Crime and Corruption Reporting Project",
    author_email="data@occrp.org",
    url="https://followthemoney.readthedocs.io/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    namespace_packages=[],
    include_package_data=True,
    package_data={"": ["followthemoney/schema/*", "followthemoney/translations/*"]},
    zip_safe=False,
    install_requires=[
        "babel >= 2.9.1, < 3.0.0",
        "pyyaml >= 5.0.0, < 6.0.0",
        "banal >= 1.0.1, < 1.1.0",
        "click >= 7.0, < 9.0.0",
        "stringcase >= 1.2.0, < 2.0.0",
        "requests >= 2.21.0, < 3.0.0",
        "fuzzywuzzy[speedup] >= 0.18.0, < 1.0.0",
        "python-levenshtein >= 0.12.0, < 1.0.0",
        "normality >= 2.1.1, < 3.0.0",
        "sqlalchemy >= 1.2.0, < 2.0.0",
        "countrynames >= 1.9.1, < 2.0.0",
        "languagecodes >= 1.0.9, < 2.0.0",
        "prefixdate >= 0.4.0, < 1.0.0",
        "fingerprints >= 1.0.1, < 2.0.0",
        "phonenumbers >= 8.12.22, < 9.0.0",
        "python-stdnum >= 1.16, < 2.0.0",
        "pantomime >= 0.4.0, < 1.0.0",
        "pytz >= 2021.1",
<<<<<<< HEAD
        "rdflib >= 6.0.0, < 6.1.0",
        "networkx >=2.5, < 2.6",
=======
        "rdflib >= 5.0.0, < 6.1.0",
        "networkx >=2.5, < 2.7",
>>>>>>> 4db9ebe22fc0bfcb580a95245f324c48a2762f55
        "openpyxl >= 3.0.5, < 4.0.0",
    ],
    extras_require={
        "dev": [
            "pip>=10.0.0",
            "bump2version",
            "wheel>=0.29.0",
            "twine",
            "flake8>=2.6.0",
            "nose",
            "transifex-client",
            "responses>=0.9.0",
            "coverage>=4.1",
            "recommonmark>=0.4.0",
        ],
        "misp": [
            "pymisp >= 2.4.126",
        ],
    },
    test_suite="nose.collector",
    entry_points={
        "babel.extractors": {"ftmmodel = followthemoney.messages:extract_yaml"},
        "followthemoney.cli": {
            "aggregate = followthemoney.cli.aggregate:aggregate",
            "sieve = followthemoney.cli.sieve:sieve",
            "link = followthemoney.cli.dedupe:link",
            "mapping = followthemoney.cli.mapping:run_mapping",
            "csv = followthemoney.cli.exports:export_csv",
            "excel = followthemoney.cli.exports:export_excel",
            "rdf = followthemoney.cli.exports:export_rdf",
            "gexf = followthemoney.cli.exports:export_gexf",
            "cypher = followthemoney.cli.exports:export_cypher",
        },
        "console_scripts": [
            "ftmutil = followthemoney.cli.cli:cli",
            "ftm = followthemoney.cli.cli:cli",
            "followthemoney = followthemoney.cli.cli:cli",
        ],
    },
    tests_require=["coverage", "nose"],
)

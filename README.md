# Follow the Money

[![ftm-build](https://github.com/alephdata/followthemoney/actions/workflows/build.yml/badge.svg)](https://github.com/alephdata/followthemoney/actions/workflows/build.yml)

This repository contains a pragmatic data model for the entities most
commonly used in investigative reporting: people, companies, assets,
payments, court cases, etc.

The purpose of this is not to model reality in an ideal data model, but
rather to have a working data structure for researchers.

`followthemoney` also contains code used to validate and normalize many
of the elements of data, and to map tabular data into the model.

## Documentation

For a general introduction to `followthemoney`, check the high-level introduction:

* https://docs.alephdata.org/developers/followthemoney

Part of this package is a command-line tool that can be used to process and
transform data in various ways. You can find a tutorial here:

* https://docs.alephdata.org/developers/ftm

Besides the introductions, there is also a full reference documentation for the
library and the contained ontology: 

* https://followthemoney.readthedocs.io/

There's also a number of viewers for the RDF schema definitions generated
from FollowTheMoney, e.g.:

* [LODE documentation](http://150.146.207.114/lode/extract?url=https%3A%2F%2Falephdata.github.io%2Ffollowthemoney%2Fns%2Fftm.xml&owlapi=true&imported=true&lang=en)
* [WebVOWL](https://service.tib.eu/webvowl/#iri=https://alephdata.github.io/followthemoney/ns/ftm.xml)
* RDF/OWL specification in [XML](https://alephdata.github.io/followthemoney/ns/ftm.xml).

## Development environment

For local development with a virtualenv:

```bash
python3 -mvenv .env
source .env/bin/activate
pip install -e ".[dev]"
```

Now you can run the tests with

```bash
make test
```

## Releasing

We release a lot of version of `followthemoney` because even small changes
to the code base require a pypi release to begin being used in `aleph`. To
this end, here's the steps for making a release:

```bash
git pull --rebase
make build
make test
git add . && git commit -m "Updating translation files"
bumpversion patch
git push --atomic origin main $(git describe --tags --abbrev=0)
```

This will create a new patch release and upload a distribution of it. If
the changes are more significant, you can run `bumpversion` with the `minor`
or `major` arguments.

When the schema is updated, please update the docs, ideally including the
diagrams. For the RDF namespace and JavaScript version of the model, 
run `make generate`.

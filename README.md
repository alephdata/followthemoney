# Follow the Money

[![Build Status](https://travis-ci.org/alephdata/followthemoney.png?branch=master)](https://travis-ci.org/alephdata/followthemoney)

This repository contains a pragmatic data model for the entities most
commonly used in investigative reporting: people, companies, assets,
payments, court cases, etc.

The purpose of this is not to model reality in an ideal data model, but
rather to have a working data structure for researchers.

`followthemoney` also contains code used to validate and normalize many
of the elements of data, and to map tabular data into the model.

## Documentation

For a general introduction to `followthemoney`, check the main documentation:

* https://docs.alephdata.org/developers/followthemoney

Part of this package is a command-line tool that can be used to process and
transform data in various ways. This is documented here:

* https://docs.alephdata.org/developers/ftm

There's no built-in tooling to render the model metadata (i.e. the list of
schemata). However, we can export the schema to RDF (RDF/OWL), the abstract
data model behind linked data. There's a number of viewers for the RDF schema
definitions generated from FollowTheMoney, e.g.:

* [LODE documentation](http://150.146.207.114/lode/extract?url=https%3A%2F%2Falephdata.github.io%2Ffollowthemoney%2Fns%2Fftm.xml&owlapi=true&imported=true&lang=en)
* [WebVOWL](http://www.visualdataweb.de/webvowl/#iri=https://alephdata.github.io/followthemoney/ns/ftm.xml)
* Raw RDF, [XML](https://alephdata.github.io/followthemoney/ns/ftm.xml) or 
  [Turtle](https://alephdata.github.io/followthemoney/ns/ftm.ttl)

## Releasing

We release a lot of version of `followthemoney` because even small changes
to the code base require a pypi release to begin being used in `aleph`. To
this end, here's the steps for making a release:

```bash
git pull --rebase
make test
bumpversion patch
git push --tags
```

This will create a new patch release and upload a distribution of it. If
the changes are more significant, you can run `bumpversion` with the `minor`
or `major` arguments.

When the schema is updated, please update the docs, ideally including the
diagrams. For the RDF namespace and JavaScript version of the model, 
run `make generate`.

# Follow the Money

[![Build Status](https://travis-ci.org/alephdata/followthemoney.png?branch=master)](https://travis-ci.org/alephdata/followthemoney)

This repository contains a pragmatic data model for the entities most
commonly used in investigative reporting: people, companies, assets,
payments, court cases, etc.

The purpose of this is not to model reality in an ideal data model, but
rather to have a working data structure for researchers.

`followthemoney` also contains code used to validate and normalize many
of the elements of data, and to map tabular data into the model.

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

## Docs

When the schema is updated, please update the docs, ideally including the diagrams.

For the RDF namespace run `make namespace`.

Namespace URI is `https://w3id.org/ftm/`. Docs are auto-hosted on github pages, and redirects are managed at https://github.com/perma-id/w3id.org/

## Command-line utility

This package installs ``ftm``, a command line utility for working with
``followthemoney``-formatted entity graph data.

### Input and output stream types

``ftm`` is based on the idea of streamed graph data that is piped between
small sub-commands. Unfortunately, there is not one single data format
that is appropriate for all stages of the utility. Instead, the following 
formats are used:

* Entity streams. An iterator of line-based JSON representations of
  ``followthemoney`` entities.
* Result streams. A set of results from an enrichment process. Each
  JSON-formatted line may include multiple entities, one of which is
  the entity being enriched (``subject``), the main match entity
  (``candidate``) and other entities that the remote API may have
  returned.
* Recon files. These files define a mapping from a source entity ID
  to a canonical entity ID, e.g. after a de-duplication process has
  been applied.

### Other commands

* ``export-cypher`` - Dump a Neo4j OpenCypher script.
* ``export-excel`` - Dump an Excel file, one sheet per schema.
* ``export-gexf`` - Dump a GEXF graph file.
* ``apply-recon`` - Read a recon file and re-write entity stream to
  their canonical ID. Should be followed by ``aggregate``.
* ``filter-results`` - Read a recon file and emit only results where
  candidate and subject are confirmed matches.

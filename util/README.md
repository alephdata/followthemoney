# FollowTheMoney command-line utility

This package installs ``ftmutil``, a command line utility for working
with ``followthemoney``-formatted entity graph data.

## Input and output stream types

``ftmutil`` is based on the idea of streamed graph data that is piped
between small sub-commands. Unfortunately, there is not one single data
format that is appropriate for all stages of the utility. Instead, the
following formats are used:

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

## Ideas for commands

* ``apply-recon`` - Read a recon file and re-write entity stream to
  their canonical ID. Should be followed by ``aggregate``.
* ``filter-results`` - Read a recon file and emit only results where
  candidate and subject are confirmed matches.
* ``recon-auto`` - Write a recon file by marking all results above a
  certain score as matches.
* ``recon-tool`` - Interactive tool for making a recon file from a set
  of results.
* ``export-cypher`` - Dump a Neo4j script.
* ``export-excel`` - Dump an Excel file, one sheet per schema.

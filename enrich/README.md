# Enrichment framework

A common use case in investigative reporting is to research a given set of companies
or people by searching for their ownership, control and other relationships in
online databases. ``enrich`` augments that process by automating look-ups in
web services and building a network graph out of the resulting set of links. It
also provides an explicit way to accept and reject results from online research,
thus making sure the entire resulting graph is fact-checked.

## Installation

Environment variables used:

* ENRICH_ALEPH_HOST
* ENRICH_ALEPH_API_KEY
* ENRICH_ORBIS_USERNAME
* ENRICH_ORBIS_PASSWORD
* ENRICH_OPENCORPORATES_API_TOKEN

Caching can be configured programmatically when the framework is used as a library,
or via a set of environment variables:

* ENRICH_CACHE_REDIS_URL
* ENRICH_CACHE_DATABASE_URL
* ENRICH_CACHE_DATABASE_TABLE

# corpint

Corporate open-source intelligence toolkit for data-driven investigations.

A common use case in investigative reporting is to research a given set of companies
or people by searching for their ownership, control and other relationships in
online databases. ``corpint`` augments that process by automating look-ups in
web services and building a network graph out of the resulting set of links. It
also provides an explicit way to accept and reject results from online research,
thus making sure the entire resulting graph is fact-checked.

## Installation

Environment variables used:

* CORPINT_ALEPH_HOST
* CORPINT_ALEPH_API_KEY
* CORPINT_ORBIS_USERNAME
* CORPINT_ORBIS_PASSWORD
* CORPINT_OPENCORPORATES_API_TOKEN
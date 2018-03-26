# Follow the Money

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
$ git pull --rebase
$ make test
$ bumpversion patch
$ make clean release
```

This will create a new patch release and upload a distribution of it. If
the changes are more significant, you can run `bumpversion` with the `minor`
or `major` arguments.
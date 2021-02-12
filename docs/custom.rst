Installing custom schema
==========================

`FollowTheMoney` lives a double life, both as a data modelling and validation tool and as a 
specific data model. While the FtM model is tailored very specifically to the practice of
investigative journalism as it is exercised in OCCRP, the FtM data modelling tool is reusable
beyond that domain. Users from adjacent fields, such as human rights advocacy, cyber forensics
or social media analysis might wish to adapt the data model.

Operators can modify the active FtM model by setting the environment variable `FTM_MODEL_PATH`
to a directory that contains a set of YAML schema description files. The simplest way to do 
this would be to download the existing YAML schema set from FtM source (`followthemoney/schema`),
and make edits in a new directory. 

This, however, raises an icky question: how mutable is the FtM model in reality? FtM itself uses
specific schemata in its tests, but that wouldn't be a fatal hindrance. However, the `aleph` and
`ingestors` applications have built-in assumptions about a larger subsection of the schema. For
example, `ingestors` require all schemata descendant from `Document` and `Mention`. Aleph assumes
that the `LegalEntity`, `Person` and `Document` types exist.

In practice, we would recommend these policies when modifying the FtM model in an Aleph deployment:

* Add schemata and properties, don't remove or rename the existing ones. 
* Don't add too many schemata. Each schema will add a new index in Aleph's ElasticSearch, and each
  index needs to be queried individually. Add 10 or 20 schemata, not 200.
* Contribute upstream: once you have successfully modelled some data into an extension of FtM,
  please feel free to submit a pull request to FtM to have them adopted into the main repo.

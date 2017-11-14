# The Schema

The followthemoney data model is designed to organise concepts which arise in money laundering and corruption investigations, in a way that is useful to investigative journalists.

The root of the data model is **Things** and **Intervals**. You can also think of these as entities and events. Things are documents, assets, legal entites and their descendents. Intervals are business interests, court cases, sanctions and transactions (and their descendents). Intervals tend to be useful for linking two entities together, possibly over a specific time period.

## Thing

![The Things schema](https://raw.githubusercontent.com/alephdata/followthemoney/master/docs/schema_thing.png)

## Interval

![The Intervals schema](https://raw.githubusercontent.com/alephdata/followthemoney/master/docs/schema_interval.png)

## Uses

This data model is used by [Aleph](https://github.com/alephdata/aleph).

## Future

Things to consider in future iterations.

* Concession is a type of contract and should share many of the properties of Contract (according to Lejla). Maybe move it from Asset to Contract.

* Event (extends Interval)
  * location
  * country

* Linking Ownership events to Transactions (Contracts and Payments) to facilitate building a timeline of how assets change hands.
# Follow The Money

The followthemoney data model is designed to organise concepts which arise in money laundering and corruption investigations, in a way that is useful to investigative journalists.

## The Schema

The root of the data model is **Things** and **Intervals**. You can also think of these as entities and events. Things are documents, assets, legal entites and their descendents. Intervals are business interests, court cases, sanctions and transactions (and their descendents). Intervals tend to be useful for linking two entities together, possibly over a specific time period.

### Thing

<img alt="The Thing schema" src="https://docs.google.com/drawings/d/e/2PACX-1vT7D6livwkAobwBgLEivm1uof2N2SP4heVMK87Q77uQ2hqz5XJrgc3vI4uWD2M4e30e59LhodqPpK29/pub?w=1762&amp;h=1113">

### Interval

<img alt="The Interval schema" src="https://docs.google.com/drawings/d/e/2PACX-1vR9vlUEfPC_zuymx0HMI2IHpViJC-c0BQI5zTlvJKFxP-z50McU5N6LPaXWMH2EHN6Nr1WJC-t561OR/pub?w=2002&amp;h=818">

## Behaviour

The YAML definitions for the schema include ways to define the behaviour or features of entities and their properties. These keys on entities are:

* `abstract` (bool): if `true`, nothing should use this as its type directly, always use a descendant. 
* `description`: an explanation of what this type of entity means.
* `extends` (string): a parent schema from which properties are inherited.
* `featured` (list): this list of properties are extra useful in understanding the entity. In Aleph we use this to decide to show properties of something even if there's no value set.
* `fuzzy` (bool): ..
* `icon` (string): the Font Awesome icon of an entity.
* `label` (string): human-friendly name for the entity type.
* `plural` (string): plural of `label`.

And on properties of entities: 

* `caption` (bool): if `true` this is the sort of property that you might want to use as the header of a web page about the thing, for example.
* `description`: an explanation of what this property means.
* `label` (string): human-friendly name for the property.
* `multiple` (bool): if `true`, can have multiple values.
* `reverse` (string): inverse of `label`
* `schema` (string): if `type` is `entity`, this is what kind. AKA 'domain' of the property.
* `type` (string): datatype of the value of this property according to [exactitude](https://github.com/alephdata/exactitude).

## Uses

This data model is used by [Aleph](https://github.com/alephdata/aleph).

## Namespace

To use this schema with RDF see the [namespace docs](ns/).

## Future

Things to consider in future iterations.

* Family relations

* Event (extends Interval)
  * location
  * country

* Linking Ownership events to Contracts and Payments to facilitate building a timeline of how assets change hands.
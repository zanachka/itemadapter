# itemadapter
[![version](https://img.shields.io/pypi/v/itemadapter.svg)](https://pypi.python.org/pypi/itemadapter)
[![pyversions](https://img.shields.io/pypi/pyversions/itemadapter.svg)](https://pypi.python.org/pypi/itemadapter)
[![actions](https://github.com/scrapy/itemadapter/workflows/Tests/badge.svg)](https://github.com/scrapy/itemadapter/actions)
[![codecov](https://codecov.io/gh/scrapy/itemadapter/branch/master/graph/badge.svg)](https://codecov.io/gh/scrapy/itemadapter)


The `ItemAdapter` class is a wrapper for data container objects, providing a
common interface to handle objects of different types in an uniform manner,
regardless of their underlying implementation.

Currently supported types are:

* [`scrapy.item.Item`](https://docs.scrapy.org/en/latest/topics/items.html#scrapy.item.Item)
* [`dict`](https://docs.python.org/3/library/stdtypes.html#dict)
* [`dataclass`](https://docs.python.org/3/library/dataclasses.html)-based classes
* [`attrs`](https://www.attrs.org)-based classes
* [`pydantic`](https://pydantic-docs.helpmanual.io/)-based classes

Additionally, interaction with arbitrary types is supported, by implementing
a pre-defined interface (see [extending `itemadapter`](#extending-itemadapter)).

---

## Requirements

* Python 3.9+, either the CPython implementation (default) or the PyPy
  implementation
* [`scrapy`](https://scrapy.org/) 2.2+: optional, needed to interact with
  `scrapy` items
* [`attrs`](https://pypi.org/project/attrs/) 20.1.0+: optional, needed to
  interact with `attrs`-based items
* [`pydantic`](https://pypi.org/project/pydantic/) 1.8+: optional, needed to
  interact with `pydantic`-based items

---

## Installation

`itemadapter` is available on [`PyPI`](https://pypi.python.org/pypi/itemadapter), it can be installed with `pip`:

```
pip install itemadapter
```

For `attrs`, `pydantic` and `scrapy` support, install the corresponding extra
to ensure that a supported version of the corresponding dependencies is
installed. For example:

```
pip install itemadapter[scrapy]
```

Mind that you can install multiple extras as needed. For example:

```
pip install itemadapter[attrs,pydantic,scrapy]
```

---

## License

`itemadapter` is distributed under a [BSD-3](https://opensource.org/licenses/BSD-3-Clause) license.

---

## Basic usage

The following is a simple example using a `dataclass` object.
Consider the following type definition:

```python
>>> from dataclasses import dataclass
>>> from itemadapter import ItemAdapter
>>> @dataclass
... class InventoryItem:
...     name: str
...     price: float
...     stock: int
>>>
```

An `ItemAdapter` object can be treated much like a dictionary:

```python
>>> obj = InventoryItem(name='foo', price=20.5, stock=10)
>>> ItemAdapter.is_item(obj)
True
>>> adapter = ItemAdapter(obj)
>>> len(adapter)
3
>>> adapter["name"]
'foo'
>>> adapter.get("price")
20.5
>>>
```

The wrapped object is modified in-place:
```python
>>> adapter["name"] = "bar"
>>> adapter.update({"price": 12.7, "stock": 9})
>>> adapter.item
InventoryItem(name='bar', price=12.7, stock=9)
>>> adapter.item is obj
True
>>>
```

### Converting to dict

The `ItemAdapter` class provides the `asdict` method, which converts
nested items recursively. Consider the following example:

```python
>>> from dataclasses import dataclass
>>> from itemadapter import ItemAdapter
>>> @dataclass
... class Price:
...     value: int
...     currency: str
>>> @dataclass
... class Product:
...     name: str
...     price: Price
>>>
```

```python
>>> item = Product("Stuff", Price(42, "UYU"))
>>> adapter = ItemAdapter(item)
>>> adapter.asdict()
{'name': 'Stuff', 'price': {'value': 42, 'currency': 'UYU'}}
>>>
```

Note that just passing an adapter object to the `dict` built-in also works,
but it doesn't traverse the object recursively converting nested items:

```python
>>> dict(adapter)
{'name': 'Stuff', 'price': Price(value=42, currency='UYU')}
>>>
```

---

## API reference

### Built-in adapters

The following adapters are included by default:

* `itemadapter.adapter.ScrapyItemAdapter`: handles `Scrapy` items
* `itemadapter.adapter.DictAdapter`: handles `Python` dictionaries
* `itemadapter.adapter.DataclassAdapter`: handles `dataclass` objects
* `itemadapter.adapter.AttrsAdapter`: handles `attrs` objects
* `itemadapter.adapter.PydanticAdapter`: handles `pydantic` objects

### class `itemadapter.adapter.ItemAdapter(item: Any)`

This is the main entrypoint for the package. Tipically, user code
wraps an item using this class, and proceeds to handle it with the provided interface.
`ItemAdapter` implements the
[`MutableMapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping)
interface, providing a `dict`-like API to manipulate data for the object it wraps
(which is modified in-place).

**Attributes**

#### class attribute `ADAPTER_CLASSES: Iterable`

Stores the currently registered adapter classes.

The order in which the adapters are registered is important. When an `ItemAdapter` object is
created for a specific item, the registered adapters are traversed in order and the first
adapter class to return `True` for the `is_item` class method is used for all subsequent
operations. The default order is the one defined in the
[built-in adapters](#built-in-adapters) section.

The default implementation uses a
[`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque)
to support efficient addition/deletion of adapters classes to both ends, but if you are
deriving a subclass (see the section on [extending itemadapter](#extending-itemadapter)
for additional information), any other iterable (e.g. `list`, `tuple`) will work.

**Methods**

#### class method `is_item(item: Any) -> bool`

Return `True` if any of the registed adapters can handle the item
(i.e. if any of them returns `True` for its `is_item` method with
`item` as argument), `False` otherwise.

#### class method `is_item_class(item_class: type) -> bool`

Return `True` if any of the registered adapters can handle the item class
(i.e. if any of them returns `True` for its `is_item_class` method with
`item_class` as argument), `False` otherwise.

#### class method `get_field_meta_from_class(item_class: type, field_name: str) -> MappingProxyType`

Return a [`types.MappingProxyType`](https://docs.python.org/3/library/types.html#types.MappingProxyType)
object, which is a read-only mapping with metadata about the given field. If the item class does not
support field metadata, or there is no metadata for the given field, an empty object is returned.

The returned value is taken from the following sources, depending on the item type:

  * [`scrapy.item.Field`](https://docs.scrapy.org/en/latest/topics/items.html#item-fields)
    for `scrapy.item.Item`s
  * [`dataclasses.field.metadata`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field)
    for `dataclass`-based items
  * [`attr.Attribute.metadata`](https://www.attrs.org/en/stable/examples.html#metadata)
    for `attrs`-based items
  * [`pydantic.fields.FieldInfo`](https://pydantic-docs.helpmanual.io/usage/schema/#field-customisation)
    for `pydantic`-based items

#### class method `get_field_names_from_class(item_class: type) -> Optional[list[str]]`

Return a list with the names of all the fields defined for the item class.
If an item class doesn't support defining fields upfront, None is returned.

#### class method `get_json_schema(item_class: type) -> dict[str, Any]`

Return a dict with a [JSON Schema](https://json-schema.org/) representation of
the item class.

The generated JSON Schema reflects field type hints, attribute docstrings and
class and field metadata of any supported item class. It also supports using
item classes in field types of other item classes.

For example, given:

```python
from dataclasses import dataclass

import attrs


@dataclass
class Brand:
    name: str

@attrs.define
class Product:
    name: str
    """Product name"""

    brand: Brand | None
    in_stock: bool = True
```

`ItemAdapter.get_json_schema(Product)` returns:

```python
{
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string", "description": "Product name"},
        "brand": {
            "anyOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ]
        },
        "in_stock": {"default": True, "type": "boolean"},
    },
    "required": ["name", "brand"],
}
```

You can also extend or override JSON Schema data at the item class or field
level:

-   Set `json_schema_extra` in field metadata to extend or override the JSON
    Schema data for that field. For example:

    ```python
    >>> from scrapy.item import Item, Field
    >>> from itemadapter import ItemAdapter
    >>> class MyItem(Item):
    ...     name: str = Field(json_schema_extra={"minLength": 1})
    ...
    >>> ItemAdapter.get_json_schema(MyItem)
    {'type': 'object', 'additionalProperties': False, 'properties': {'name': {'minLength': 1, 'type': 'string'}}, 'required': ['name']}

    ```

-   Define a `__json_schema_extra__` class attribute dict to extend or override
    JSON Schema data for the entire class. For example:

    ```python
    >>> from dataclasses import dataclass
    >>> from itemadapter import ItemAdapter
    >>> @dataclass
    ... class MyItem:
    ...     __json_schema_extra__ = {"additionalProperties": True}
    ...     name: str
    ...
    >>> ItemAdapter.get_json_schema(MyItem)
    {'additionalProperties': True, 'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}

    ```

Note that, for Pydantic items, itemadapter does not use
[`model_json_schema()`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_json_schema)
and instead uses its own implementation. That way, the output JSON Schema is
consistent across different item types. It also makes it possible to generate
JSON Schemas for Pydantic models that have nested non-Pydantic item classes as
fields. The downside is that JSON Schema support in itemadapter may not be as
advanced as Pydantic‘s.

The following are some known limitations of JSON Schema generation in
itemadapter:

-   Attribute docstrings are read with
    [`inspect.getsource()`](https://docs.python.org/3/library/inspect.html#inspect.getsource),
    and may not be readable at run time in some cases. For such cases, define
    `description` within `json_schema_extra` instead (see below).

-   String pattern contraints are silently ignored if they are not compatible
    with JSON Schema. No effort is made to make them compatible.

-   Recursion is silently ignored: if you have an item class that has an
    attribute with that same item class as a type or as part of its type, a
    simple `{"type": "object"}` is used to map the nested instances of that
    item class.

#### `get_field_meta(field_name: str) -> MappingProxyType`

Return metadata for the given field, if available. Unless overriden in a custom adapter class, by default
this method calls the adapter's `get_field_meta_from_class` method, passing the wrapped item's class.

#### `field_names() -> collections.abc.KeysView`

Return a [keys view](https://docs.python.org/3/library/collections.abc.html#collections.abc.KeysView)
with the names of all the defined fields for the item.

#### `asdict() -> dict`

Return a `dict` object with the contents of the adapter. This works slightly different than
calling `dict(adapter)`, because it's applied recursively to nested items (if there are any).


### function `itemadapter.utils.is_item(obj: Any) -> bool`

Return `True` if the given object belongs to (at least) one of the supported types,
`False` otherwise. This is an alias, using the `itemadapter.adapter.ItemAdapter.is_item`
class method is encouraged for better performance.


### function `itemadapter.utils.get_field_meta_from_class(item_class: type, field_name: str) -> types.MappingProxyType`

Alias for `itemadapter.adapter.ItemAdapter.get_field_meta_from_class`

---

## Metadata support

`scrapy.item.Item`, `dataclass`, `attrs`, and `pydantic` objects allow the definition of
arbitrary field metadata. This can be accessed through a
[`MappingProxyType`](https://docs.python.org/3/library/types.html#types.MappingProxyType)
object, which can be retrieved from an item instance with
`itemadapter.adapter.ItemAdapter.get_field_meta`, or from an item class
with the `itemadapter.adapter.ItemAdapter.get_field_meta_from_class`
method (or its alias `itemadapter.utils.get_field_meta_from_class`).
The source of the data depends on the underlying type (see the docs for
`ItemAdapter.get_field_meta_from_class`).

#### `scrapy.item.Item` objects

```python
>>> from scrapy.item import Item, Field
>>> from itemadapter import ItemAdapter
>>> class InventoryItem(Item):
...     name = Field(serializer=str)
...     value = Field(serializer=int, limit=100)
...
>>> adapter = ItemAdapter(InventoryItem(name="foo", value=10))
>>> adapter.get_field_meta("name")
mappingproxy({'serializer': <class 'str'>})
>>> adapter.get_field_meta("value")
mappingproxy({'serializer': <class 'int'>, 'limit': 100})
>>>
```

#### `dataclass` objects

```python
>>> from dataclasses import dataclass, field
>>> @dataclass
... class InventoryItem:
...     name: str = field(metadata={"serializer": str})
...     value: int = field(metadata={"serializer": int, "limit": 100})
...
>>> adapter = ItemAdapter(InventoryItem(name="foo", value=10))
>>> adapter.get_field_meta("name")
mappingproxy({'serializer': <class 'str'>})
>>> adapter.get_field_meta("value")
mappingproxy({'serializer': <class 'int'>, 'limit': 100})
>>>
```

#### `attrs` objects

```python
>>> import attr
>>> @attr.s
... class InventoryItem:
...     name = attr.ib(metadata={"serializer": str})
...     value = attr.ib(metadata={"serializer": int, "limit": 100})
...
>>> adapter = ItemAdapter(InventoryItem(name="foo", value=10))
>>> adapter.get_field_meta("name")
mappingproxy({'serializer': <class 'str'>})
>>> adapter.get_field_meta("value")
mappingproxy({'serializer': <class 'int'>, 'limit': 100})
>>>
```

#### `pydantic` objects

```python
>>> from pydantic import BaseModel, Field
>>> class InventoryItem(BaseModel):
...     name: str = Field(json_schema_extra={"serializer": str})
...     value: int = Field(json_schema_extra={"serializer": int, "limit": 100})
...
>>> adapter = ItemAdapter(InventoryItem(name="foo", value=10))
>>> adapter.get_field_meta("name")
mappingproxy({'annotation': <class 'str'>, 'json_schema_extra': {'serializer': <class 'str'>}, 'repr': True})
>>> adapter.get_field_meta("value")
mappingproxy({'annotation': <class 'int'>, 'json_schema_extra': {'serializer': <class 'int'>, 'limit': 100}, 'repr': True})
>>>
```

---

## Extending `itemadapter`

This package allows to handle arbitrary item classes, by implementing an adapter interface:

_class `itemadapter.adapter.AdapterInterface(item: Any)`_

Abstract Base Class for adapters. An adapter that handles a specific type of item must
inherit from this class and implement the abstract methods defined on it. `AdapterInterface`
inherits from [`collections.abc.MutableMapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping),
so all methods from the `MutableMapping` interface must be implemented as well.

* _class method `is_item_class(cls, item_class: type) -> bool`_

    Return `True` if the adapter can handle the given item class, `False` otherwise. Abstract (mandatory).

* _class method `is_item(cls, item: Any) -> bool`_

    Return `True` if the adapter can handle the given item, `False` otherwise.
    The default implementation calls `cls.is_item_class(item.__class__)`.

* _class method `get_field_meta_from_class(cls, item_class: type) -> bool`_

    Return metadata for the given item class and field name, if available.
    By default, this method returns an empty `MappingProxyType` object. Please supply your
    own method definition if you want to handle field metadata based on custom logic.
    See the [section on metadata support](#metadata-support) for additional information.

* _method `get_field_meta(self, field_name: str) -> types.MappingProxyType`_

    Return metadata for the given field name, if available. It's usually not necessary to
    override this method, since the `itemadapter.adapter.AdapterInterface` base class
    provides a default implementation that calls `ItemAdapter.get_field_meta_from_class`
    with the wrapped item's class as argument.
    See the [section on metadata support](#metadata-support) for additional information.

* _method `field_names(self) -> collections.abc.KeysView`_:

    Return a [dynamic view](https://docs.python.org/3/library/collections.abc.html#collections.abc.KeysView)
    of the item's field names. By default, this method returns the result of calling `keys()` on
    the current adapter, i.e., its return value depends on the implementation of the methods from the
    `MutableMapping` interface (more specifically, it depends on the return value of `__iter__`).

    You might want to override this method if you want a way to get all fields for an item, whether or not
    they are populated. For instance, Scrapy uses this method to define column names when exporting items to CSV.

### Registering an adapter

Add your custom adapter class to the
`itemadapter.adapter.ItemAdapter.ADAPTER_CLASSES` class attribute in order to
handle custom item classes.

**Example**
```
pip install zyte-common-items
```
```python
>>> from itemadapter.adapter import ItemAdapter
>>> from zyte_common_items import Item, ZyteItemAdapter
>>>
>>> ItemAdapter.ADAPTER_CLASSES.appendleft(ZyteItemAdapter)
>>> item = Item()
>>> adapter = ItemAdapter(item)
>>> adapter
<ItemAdapter for Item()>
>>>
```

### Multiple adapter classes

If you need to have different handlers and/or priorities for different cases
you can subclass the `ItemAdapter` class and set the `ADAPTER_CLASSES`
attribute as needed:


**Example**
```python
>>> from itemadapter.adapter import (
...     ItemAdapter,
...     AttrsAdapter,
...     DataclassAdapter,
...     DictAdapter,
...     PydanticAdapter,
...     ScrapyItemAdapter,
... )
>>> from scrapy.item import Item, Field
>>>
>>> class BuiltinTypesItemAdapter(ItemAdapter):
...     ADAPTER_CLASSES = [DictAdapter, DataclassAdapter]
...
>>> class ThirdPartyTypesItemAdapter(ItemAdapter):
...     ADAPTER_CLASSES = [AttrsAdapter, PydanticAdapter, ScrapyItemAdapter]
...
>>> class ScrapyItem(Item):
...     foo = Field()
...
>>> BuiltinTypesItemAdapter.is_item(dict())
True
>>> ThirdPartyTypesItemAdapter.is_item(dict())
False
>>> BuiltinTypesItemAdapter.is_item(ScrapyItem(foo="bar"))
False
>>> ThirdPartyTypesItemAdapter.is_item(ScrapyItem(foo="bar"))
True
>>>
```

---

## More examples

### `scrapy.item.Item` objects

```python
>>> from scrapy.item import Item, Field
>>> from itemadapter import ItemAdapter
>>> class InventoryItem(Item):
...     name = Field()
...     price = Field()
...
>>> item = InventoryItem(name="foo", price=10)
>>> adapter = ItemAdapter(item)
>>> adapter.item is item
True
>>> adapter["name"]
'foo'
>>> adapter["name"] = "bar"
>>> adapter["price"] = 5
>>> item
{'name': 'bar', 'price': 5}
>>>
```

### `dict`

```python
>>> from itemadapter import ItemAdapter
>>> item = dict(name="foo", price=10)
>>> adapter = ItemAdapter(item)
>>> adapter.item is item
True
>>> adapter["name"]
'foo'
>>> adapter["name"] = "bar"
>>> adapter["price"] = 5
>>> item
{'name': 'bar', 'price': 5}
>>>
```

### `dataclass` objects

```python
>>> from dataclasses import dataclass
>>> from itemadapter import ItemAdapter
>>> @dataclass
... class InventoryItem:
...     name: str
...     price: int
...
>>> item = InventoryItem(name="foo", price=10)
>>> adapter = ItemAdapter(item)
>>> adapter.item is item
True
>>> adapter["name"]
'foo'
>>> adapter["name"] = "bar"
>>> adapter["price"] = 5
>>> item
InventoryItem(name='bar', price=5)
>>>
```

### `attrs` objects

```python
>>> import attr
>>> from itemadapter import ItemAdapter
>>> @attr.s
... class InventoryItem:
...     name = attr.ib()
...     price = attr.ib()
...
>>> item = InventoryItem(name="foo", price=10)
>>> adapter = ItemAdapter(item)
>>> adapter.item is item
True
>>> adapter["name"]
'foo'
>>> adapter["name"] = "bar"
>>> adapter["price"] = 5
>>> item
InventoryItem(name='bar', price=5)
>>>
```

### `pydantic` objects

```python
>>> from pydantic import BaseModel
>>> from itemadapter import ItemAdapter
>>> class InventoryItem(BaseModel):
...     name: str
...     price: int
...
>>> item = InventoryItem(name="foo", price=10)
>>> adapter = ItemAdapter(item)
>>> adapter.item is item
True
>>> adapter["name"]
'foo'
>>> adapter["name"] = "bar"
>>> adapter["price"] = 5
>>> item
InventoryItem(name='bar', price=5)
>>>
```


## Changelog

See the [full changelog](Changelog.md)

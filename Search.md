The DataGrid search expressions use Python syntax for selecting matching
rows. To use the value of a column in the expression, just use the
name of the column like this `score`, or if it has a space in it, like
this `column__1`. Some examples:

To select all of the rows that have a fitness score less than 0.1,
given that you have a column named "Fitness":

```python
fitness < 0.1
```

Note that the column name is case-insensitive (i.e., you can use any
case of letters). Column values can be used any where in
the filter expression. For example, if you wanted to select all of the
rows where column "Score 1" was greater than or equal to "Score 2",
you would write:

```python
score__1 >= score__2
```

You can use any of Python's operators, including:

* `<` - less than
* `<=` - less than or equal
* `>` - greater than
* `>=` - greater than or equal
* `==` - equal to
* `!=` - not equal to
* `is` - is the same (e.g., `is None`)
* `is not` - is not the same (e.g. `is not None`)
* `+` - addition
* `-` - subtraction
* `*` - multiplication
* `/` - division
* `//` - integer division
* `**` - raise to a power
* `not` - flip the boolean value
* `in` - is value in a list of values

Also you can use Python's comparison operator chaining. That is, any of the above operators can be used in a shorthand way as follows:

```python
column_a < column_b < column_c
```

which is shorthand for:

```python
column_a < column_b and column_b < column c
```

Note: the single underscore matches a literal underscore, where a double underscore matches a space, in the column name.

Use `is None` and `is not None` for selecting rows that have null values. Otherwise,
null values are ignored in most other uses.

You can combine comparisons using Python's `and` and `or` (use parentheses to force
evaluation order different from Python's defaults):

```python
((loss - base__line) < 0.5) or (loss > 0.95)
```

JSON attribute access
=====================

For JSON and metdata columns, you can use the dot
operator to access values:

```python
Image.extension == "jpg"
```

or nested values:

```python
Image.labels.dog > 2
```
The dotted-name path following a column of JSON data deviates from Python semantics. In addition, the path can only be use for nested dictionaries. If the JSON has a list, then you will not be able to use the dotted-name syntax. However, you can use Python's list comprehension, like these examples:

1. `any([x["label"] == 'dog' for x in Image.overlays])` - images with dogs
2. `all([x["label"] == 'person' for x in Image.overlays])` - images with only people (no other labels)
3. `any([x["label"] in ["car", "bicycle"] for x in Image.overlays])` - images with cars or bicycles
4. `any([x["label"] == "cat" or x["label"] == "dog" for x in Image.overlays])` - images with dogs or cats
5. `any([x["label"] == "cat" for x in Image.overlays]) and any([x["label"] == "dog" for x in Image.overlays])` - images with dogs and cats
6. `any([x["score"] > 0.999 for x in Image.overlays])` - images with an annotation score greater than 0.999

List comprehension also deviates slightly from standard Python semantics:

* `[item for item in LIST]` - same as Python (item is each element in the list)
* `[item for item in DICT]` - item is the DICT

Note that you will need to wrap the list comprehension in either `any()` or `all()`. You can also use `flatten()` around nested list comprehensions.

See below for more information on `contains()` and other string and JSON
methods.

Note that any mention of a column that contains an asset type (e.g.,
an image) will automatically reference its metadata.

Python String and JSON methods
==============================

These are mostly used with column values:

* `STRING in Column__Name`
* `Column__Name.endswith(STRING)`
* `Column__Name.startswith(STRING)`
* `Column__Name.strip()`
* `Column__Name.lstrip()`
* `Column__Name.rstrip()`
* `Column__Name.upper()`
* `Column__Name.lower()`
* `Column__Name.split(DELIM[, MAXSPLITS])`


Python if/else expression
=========================

You can use Python's if/else expression to return one
value or another.

```python
("low" if loss < 0.5 else "high") == "low"
```

Python Builtin Functions
========================

You can use any of these Python builtin functions:

* `abs()` - absolute value
* `round()` - rounds to int
* `max(v1, v2, ...)` or `max([v1, v2, ...])` - maximum of list of values
* `min(v1, v2, ...)` or `min([v1, v2, ...])` - minimum of list of values
* `len()` - length of item

Aggregate Functions
===================

You can use the following aggregate functions. Note that these
are more expensive to compute, as they require computing on all
rows.

* `AVG(Column__Name)`
* `MAX(Column__Name)`
* `MIN(Column__Name)`
* `SUM(Column__Name)`
* `TOTAL(Column__Name)`
* `COUNT(Column__Name)`
* `STDEV(Column__Name)`

Examples:

Find all rows that have a loss value less than the average:

```python
loss < AVG(loss)
```

Python Library Functions and Values
===================================

Functions from Python's `random` library:

* `random.random()`
* `random.randint()`

Note that random values are regenerated on each call, and thus
only have limited use. That means that every time the
DataGrid is accessed, the values will change. This would
result in bizarre results if you grouped or sorted by
a random value.

Functions and values from Python's `math` library:

* `math.pi`
* `math.sqrt()`
* `math.acos()`
* `math.acosh()`
* `math.asin()`
* `math.asinh()`
* `math.atan()`
* `math.atan2()`
* `math.atanh()`
* `math.ceil()`
* `math.cos()`
* `math.cosh()`
* `math.degrees()`
* `math.exp()`
* `math.floor()`
* `math.log()`
* `math.log10()`
* `math.log2()`
* `math.radians()`
* `math.sin()`
* `math.sinh()`
* `math.tan()`
* `math.tanh()`
* `math.trunc()`

Functions and values from Python's `datetime` library:

* `datetime.date(YEAR, MONTH, DAY)`
* `datetime.datetime(YEAR, MONTH, DAY[, HOUR, MINUTE, SECOND])`

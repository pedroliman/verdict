---
label: "Scale"
icon: sliders
---

## Usage
A `Scale` can be used directly in a `Schema` to specify the response format required by the scale.

||| Ordinal Scale
~~~python
class ResponseSchema(Schema):
  score: Scale = ContinuousScale(0, 1)
  # Structured Output extractor will enforce 0 <= score <= 1
~~~
||| Categorical Scale
~~~python
class ResponseSchema(Schema):
  grade: Scale = DiscreteScale(['A', 'B', 'C', 'D', 'E', 'F'])
  # Token Probability extractor will infer a distribution over A..F
~~~
|||

By default, the first value in the scale is the worst and the last value is the best. You can use the `end_is_worst` flag to flip this behavior.
```python
class ResponseSchema(Schema):
  reward: Scale = DiscreteScale((1, 5), end_is_worst=True)
  # => reward.specification_prompt()='Respond with a single output value from "1", "2", "3", "4", "5" where "1" is best and "5" is worst.'
```

## Scale Types
A `Scale` specifies a set of response values used in various stages of a judging system. In Verdict, all `Scale`s expose
- a `specification_prompt` that can be used within a prompt to specify the response format required by the scale.
  - e.g., *Respond with a single output value from “A”, “B”, “C”, “D”, “E”, “F” where “A” is worst and “F” is best.*
- a `value_mapping_fn` to map raw token output back to a value in the scale.
  - e.g., `'yes'` → `True`; `'no'` → `False`; `'1'` → `1`

### Discrete/Categorical/Ordinal
In addition to the above, a `DiscreteScale` exposes

* a discrete `token_support`
  - e.g., `['A', 'B', 'C', 'D', 'E', 'F']`
  - e.g., `['1', '2', '3']`

A DiscreteScale can either be initialized either by a range ([start, end[, step=1]]) of integers/floats/characters or an explicit list of values. The following initialization approaches are equivalent:

```python
DiscreteScale((1, 5))
DiscreteScale([1, 2, 3, 4, 5])
DiscreteScale((1, 5, 1)) # step defaults to 1
```

We also provide the `BooleanScale` for convenience, which is a `DiscreteScale` with a `token_support` of `['True', 'False']` and maps `"yes"`/`"Yes"`/`"YES"` to `True`.

### Continuous
Supports `float`s by default and can be initialized with an inclusive range `[min_value, max_value]`.

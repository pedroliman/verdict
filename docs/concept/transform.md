---
label: "Transform/Propagate"
icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="M8.75 4.75a3.25 3.25 0 1 0 6.5 0 3.25 3.25 0 0 0-6.5 0ZM15 19.25a3.25 3.25 0 1 0 6.5 0 3.25 3.25 0 0 0-6.5 0Zm-12.5 0a3.25 3.25 0 1 0 6.5 0 3.25 3.25 0 0 0-6.5 0ZM5.75 17.5a1.75 1.75 0 1 1-.001 3.501A1.75 1.75 0 0 1 5.75 17.5ZM12 3a1.75 1.75 0 1 1-.001 3.501A1.75 1.75 0 0 1 12 3Zm6.25 14.5a1.75 1.75 0 1 1-.001 3.501A1.75 1.75 0 0 1 18.25 17.5Z"/><path d="M6.5 16.25v-1A2.25 2.25 0 0 1 8.75 13h6.5a2.25 2.25 0 0 1 2.25 2.25v1H19v-1a3.75 3.75 0 0 0-3.75-3.75h-6.5A3.75 3.75 0 0 0 5 15.25v1Z"/><path d="M11.25 7.75v5h1.5v-5h-1.5Z"/></svg>
order: 8
---

While the `Unit` abstraction may feel insufficient to express complex logic or limiting, we provide two mechanisms for arbitrary Python code execution that enable quick iteration without giving up the benefits of the `Schema` type enforcement.

## Map/Transform
`MapUnit` allows you to apply an arbitrary function to the output of a `Unit`.
```python
from verdict.common.judge import JudgeUnit
from verdict.transform import MapUnit

JudgeUnit() \
    >> MapUnit(lambda judge: Schema.of(score=((judge.score / 5) * 7))) # normalize to 1-7 scale
```

It has native support for multiple dependencies, which are indexed first-come first-serve at definition-time.

||| Reduce
~~~python
from verdict import Layer

Layer(JudgeUnit(), 5) \
>> MapUnit(lambda judges: Schema.of(score=min(judge.score for judge in judges)))
~~~
||| Index
~~~python
Layer([
    JudgeUnit(DiscreteScale((1, 5), end_is_worst=False)),
    JudgeUnit(DiscreteScale((1, 5), end_is_worst=True))]) \
>> MapUnit(lambda judges: Schema.of(score=(judges[0].score + (6 - judges[1].score)) / 2))
~~~
|||

Additionally, we provide the following built-in `MapUnit`s for convenience.

{.compact}
| MapUnit | Description | Output Schema   |
| ------: | ----------- | --------------- |
| MeanPoolUnit | Compute the mean of a list of values. | `Schema.of(field_name=field_type)` |
| MaxPoolUnit | Compute the mode of a list of values. | `Schema.of(field_name=field_type` |
| MeanVariancePoolUnit | Compute the mean and variance of a list of values. | `Schema.of(mean=float, variance=float)` |

## Propagate
You can specify special logic to modify the `OutputSchema` of a `Unit` post-execution by using the `.propagate()` directive. This is particularly useful for propagating forward the `OutputSchema` of a dependency. Refer to the [Previous](./prompt.md#previous) section for more details.

||| Propagate Dependency
~~~python
from verdict.schema import Schema

ConversationalUnit("Proponent").propagate(
    lambda unit, previous, input, output: Schema.of(
        thought=previous.thought,
        conversation=output.conversation
    ))
~~~
||| MapUnit Example
~~~python
from verdict.common.judge import JudgeUnit

JudgeUnit().propagate(
    lambda unit, previous, input, output: Schema.of(
        score=(previous.score / 5) * 7
    )) \
>> ...
~~~
|||

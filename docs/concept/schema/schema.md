---
label: "Schema"
icon: note
order: 8
expanded: true
---

Inputs and outputs at all stages of execution are typed and well-specified. This lends to us a number of key benefits, such as

- formalizing and easily debugging the data flow between components in a Pipeline
- quick prototyping by mixing LLM-as-a-judge primitives with different naming conventions

We build on top of [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) and provide a number of convenience utilities to make this requirement less cumbersome.

## Helper Functions
```python
Schema.infer(score=5)    # produces a Schema type with a score field of type(5) == int
Schema.of(score=5)       # produces a Schema instance with a score field of type int and value 5
Schema.inline(score=int) # produces a Schema type with a score field of type int
Schema.empty()           # produces an Schema instance with no fields
```

Note that just like with Pydantic models, there is a distinction between a `Schema` type and a `Schema` instance.

## Native Support for Scale
You can use any [`Scale`](./scale) in your `Schema` by simply declaring it as a field.

```python
class LikertJudgeUnit(Unit):
    class ResponseSchema(Schema):
        score: Scale = DiscreteScale((1, 5)) # implicly typed as an int with ge=1, le=5
```

This will automatically convert the `score` field to the appropriate type.

## Automatic Name-Casting
We automatically attempt to cast the execution output of a `Unit` to the `InputSchema` of the next Unit in an append-only manner. This allows us to mix and match core LLM-as-a-judge primitives and common concepts to tasks with different naming conventions. For example, the following `OutputSchema` is compatible with the `InputSchema` despite different field names and orders.

!!!
This is not a destructive operation, it is append-only. We never **remove** a field from a Schema, but only copy fields to the requested field names in the target Schema if they are missing in the source Schema. We use the field type (e.g., `int`) + constraints (e.g., `ge=1`, `le=5`) to determine if a field is compatible.
!!!

```python
class JudgeUnit(Unit):
    class ResponseSchema(Schema):
        explanation: str
        score: int

class SummarizeUnit(Unit):
    class InputSchema(Schema):
        rating: int
```

At runtime, the JudgeUnit's `ResponseSchema` will be cast to the following `Schema` so that it is compatible with the `InputSchema` of the SummarizeUnit.

```python
class ResponseSchema(Schema): # conformed to SummarizeUnit.InputSchema
    explanation: str
    score: int
    rating: int # has same value as `score`
```
